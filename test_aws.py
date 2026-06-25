import boto3
import time
import sys

def main():
    iam = boto3.client('iam')
    athena = boto3.client('athena', region_name='eu-central-1')

    print("Generating CloudTrail events...")
    user_name = 'cloud-sec-audit-test-user-test1234'
    try:
        iam.create_user(UserName=user_name)
        print(f"Created user {user_name}")
        time.sleep(2)
        iam.delete_user(UserName=user_name)
        print(f"Deleted user {user_name}")
    except Exception as e:
        print(f"Error generating events: {e}")
        # Ignore errors if user exists

    # Give CloudTrail a moment to process, though logs take ~5 mins to deliver to S3.
    # The requirement is just to verify Athena works and queries can be executed.
    
    database = 'security_analytics_44i4sj'
    workgroup = 'cloud-sec-audit-prod-workgroup'
    s3_path = 's3://cloud-sec-audit-prod-logs-44i4sj/AWSLogs/217343504992/CloudTrail/'

    ddl = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS cloudtrail_logs (
        eventVersion STRING,
        userIdentity STRUCT<
            type: STRING,
            principalId: STRING,
            arn: STRING,
            accountId: STRING,
            invokedBy: STRING,
            accessKeyId: STRING,
            userName: STRING,
            sessionContext: STRUCT<
                attributes: STRUCT<
                    mfaAuthenticated: STRING,
                    creationDate: STRING>,
                sessionIssuer: STRUCT<
                    type: STRING,
                    principalId: STRING,
                    arn: STRING,
                    accountId: STRING,
                    userName: STRING>>>,
        eventTime STRING,
        eventSource STRING,
        eventName STRING,
        awsRegion STRING,
        sourceIpAddress STRING,
        userAgent STRING,
        errorCode STRING,
        errorMessage STRING,
        requestParameters STRING,
        responseElements STRING,
        additionalEventData STRING,
        requestId STRING,
        eventId STRING,
        resources ARRAY<STRUCT<
            arn: STRING,
            accountId: STRING,
            type: STRING>>,
        eventType STRING,
        apiVersion STRING,
        recipientAccountId STRING,
        serviceEventDetails STRING,
        sharedEventID STRING,
        vpcEndpointId STRING
    )
    ROW FORMAT SERDE 'com.amazon.emr.hive.serde.CloudTrailSerde'
    STORED AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
    OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
    LOCATION '{s3_path}'
    TBLPROPERTIES ('classification'='cloudtrail');
    """

    print("Creating Athena table...")
    res = athena.start_query_execution(
        QueryString=ddl,
        QueryExecutionContext={'Database': database},
        WorkGroup=workgroup
    )
    exec_id = res['QueryExecutionId']
    
    # Wait for completion
    while True:
        status = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)
        
    print(f"Table creation status: {status}")
    if status == 'FAILED':
        reason = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['StateChangeReason']
        print(f"Failed reason: {reason}")
        sys.exit(1)

    print("Running sample Athena query...")
    query = "SELECT eventName, eventTime FROM cloudtrail_logs LIMIT 5;"
    res = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database},
        WorkGroup=workgroup
    )
    exec_id = res['QueryExecutionId']
    
    while True:
        status = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)

    print(f"Query execution status: {status}")
    if status == 'FAILED':
        reason = athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']['Status']['StateChangeReason']
        print(f"Failed reason: {reason}")
        sys.exit(1)
        
    print("Test completed successfully.")

if __name__ == '__main__':
    main()
