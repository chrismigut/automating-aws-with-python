# Practice Automating AWS with Python
Practice Automating AWS with Python

*Completed checklist*
* Setup IAM role for python
* Setup Route53 for DNS domain
* Registered TLS Cert with Route53 from Certificate Manager

## 01-webotron

Webotron is a script that will sync a local directory
to an s3 bucket, and optionally configure Route 53 and
CloudFront as well.

### Features

Webotron currently has the following Features

- List buckets
- List objects in a bucket
- Setup bucket and configure
- Sync directory tree to bucket
- Set AWS profile with --profile=<profileName>
