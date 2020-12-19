# AWS.CloudWatch.Python
Gather CloudWatch Lambda Logging for Troubleshooting (Slack specific)

## amazonWebServices.ec2.python
**AWS (Amazon Web Services) ec2 instances start and stop (running and stopping) by python**

- [x] --- 說明 ---

    此程的功能為提供使用 Amazon Web Service (AWS) 的 Lambda 服務的使用者可以簡便地透過 CloudWatch 的 Logging 來識別問題。
    例如以下的 Logging 可以用 Visual Studio Code 或其他類別的工具像 https://jsonformatter.curiousconcept.com/ 來查看。

    ![範例畫面](https://github.com/spectreConstantine/AWS.CloudWatch.Python/blob/main/2020-12-20_005018.jpg)


- [x] --- 程式使用說明如下 ---

    * 參考 執行環境需求 安裝 Python3 及 boto 套件。
    * 此程式需先要用 aws cli 設定 AWS Configure, 這樣會在 %userprofile%/.aws/產生 credentials這個檔。當然你也可以自己寫。
    
      * [profile username]
      * aws_access_key_id = AKcccccccxxxxxxxx4I
      * aws_secret_access_key = nxxx88xxxxxxud2KAxm
      
- [x] --- 執行環境需求 ---

    * 電腦裡要安裝Python 3.7.7 (這是我用的版本, 其他版本也許可以跑但沒實測過).
    * 同時要安裝 boto3 (使用命令列 pip install boto3), 其他都是內建的. 
