# AWS.CloudWatch.Python
Gather CloudWatch Lambda Logging for Troubleshooting (Slack specific)

## amazonWebServices.ec2.python
**AWS (Amazon Web Services) ec2 instances start and stop (running and stopping) by python**

- [x] --- 說明 ---

    此程的功能為提供使用 Amazon Web Service (AWS) 的 Lambda 服務的使用者可以簡便地透過 CloudWatch 的 Logging 來識別問題。

    ![關機狀態](https://github.com/spectreConstantine/amazonWebServices.ec2.python/blob/master/2020-04-27_094454.png)


- [x] --- 程式使用說明如下 ---

    * 參考 執行環境需求 安裝 Python3 及 boto 套件。
    * 此程式需先要用 aws cli 設定 AWS Configure, 這樣會在 %userprofile%/.aws/產生 credentials這個檔。當然你也可以自己寫。
    
      * [profile username]
      * aws_access_key_id = AKcccccccxxxxxxxx4I
      * aws_secret_access_key = nxxx88xxxxxxud2KAxm
      
- [x] --- 執行環境需求 ---

    * 電腦裡要安裝Python 3.7.7 (這是我用的版本, 其他版本也許可以跑但沒實測過).
    * 同時要安裝 boto3 (使用命令列 pip install boto3), 其他都是內建的. 
