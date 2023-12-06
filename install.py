import launch

if not launch.is_installed("boto3"):
    launch.run_pip("install boto3==1.33.8", "requirements for s3 download api")