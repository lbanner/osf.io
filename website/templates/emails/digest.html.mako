<% from website.models import Node %>
<% from website import util %>
<%def name="build_message(d, parent=None)">
%for key in d['children']:
    %if d['children'][key]['messages']:
        <table class="block" width="100%" border="0" cellpadding="15" cellspacing="0" align="center">
            <thead class="block-head">
            <th colspan="2" style="padding: 0px 15px 0px 15px;">
                <h3 style="padding: 0 15px 5px 15px; margin: 30px 0 0 0;border: none;list-style: none;font-weight: 300; border-bottom: 1px solid #eee; text-align: left;">
                ${Node.load(key).title}
                %if parent :
                    <small style="font-size: 14px;color: #999;"> in ${Node.load(parent).title}</small>
                %endif
                </h3>
            </th>
            </thead>
            <tbody>
            <tr>
                <td style="border-collapse: collapse;">
                    %for m in d['children'][key]['messages']:
                        ${m}
                    %endfor
                </td>
            </tr>
            </tbody>
        </table>
    %endif
    %if isinstance(d['children'][key]['children'], dict):
        ${build_message(d['children'][key], key )}
    %endif
%endfor
</%def>

<html class="no-js" lang="">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>COS Email Notification Template</title>
    <meta name="description" content="Center for Open Science Notifications">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" style="-webkit-text-size-adjust: none;font-family: 'Helvetica', sans-serif;background: #eeeeee;padding: 0;margin: 0;border: none;list-style: none;width: 100% !important;">
<table id="layout-table" width="100%" border="0" cellpadding="0" cellspacing="0">
    <tr>
        <td style="border-collapse: collapse;">
            <table id="layout-table" width="100%" border="0" cellpadding="10" cellspacing="0" height="100%">
                <tbody>
                <tr class="banner" style="background: #214762;color: white;">
                    <td class="text-center" style="border-collapse: collapse;text-align: center;">
                        <table id="header-logo" border="0" style="margin: 0 auto;padding: 0px;">
                            <tr>
                                <td style="border-collapse: collapse;">
                                    <img src="https://osf.io/static/img/cos-white2.png" alt="COS logo" width="36" style="border: 0;height: auto;line-height: 100%;outline: none;text-decoration: none;">
                                </td>
                                <td style="border-collapse: collapse;">
                                    <h2 style="padding: 0;margin: 0;border: none;list-style: none;font-weight: 300;font-size: 20px;text-align: left; color: white;">Open Science Framework</h2>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                </tbody>
            </table>
        </td>
    </tr>
    <tr>
        <td style="border-collapse: collapse;">
            <table id="content" width="600" border="0" cellpadding="25" cellspacing="0" align="center" style="margin: 30px auto 0 auto;background: white;box-shadow: 0 0 2px #ccc;">
                <tbody>
                    <tr>
                        <td style="border-collapse: collapse;">
                            <h3 class="text-center" style="padding: 0;margin: 30px 0 0 0;border: none;list-style: none;font-weight: 300;text-align: center;">Recent Activity</h3>
                        </td>
                    </tr>
                    <tr>
                        <td style="border-collapse: collapse;">
                            ${build_message(message)}
                        </td>
                    </tr>
                </tbody>
            </table>
        </td>
    </tr>
    <tr>
        <td style="border-collapse: collapse;">
            <table width="80%" border="0" cellpadding="10" cellspacing="0" align="center" class="footer" style="margin-top: 45px;padding: 25px 0 35px;background-color: rgb(244, 244, 244);border-top: 1px solid #E5E5E5;border-bottom: 1px solid #E5E5E5;width: 100%;color: #555;">
                <tbody>
                <tr>
                    <td style="border-collapse: collapse;">
                        <p class="small text-center" style="text-align: center;font-size: 12px;">Copyright &copy; 2015 Center For Open Science, All rights reserved. </p>
                        <p class="small text-center" style="text-align: center;font-size: 12px; line-height: 20px;">You received this email because you are subscribed to email notifications. <br><a href="${util.web_url_for('user_notifications', _absolute=True)}" style="padding: 0;margin: 0;border: none;list-style: none;color: #008de5;text-decoration: none;font-weight: bold;">Update Subscription Preferences</a></p>
                    </td>
                </tr>
                </tbody>
            </table>
        </td>
    </tr>
</table>
</body>
</html>
