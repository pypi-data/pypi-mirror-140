from SlyGmail import *

async def test_readme():

    gmail = await Gmail('test/app.json', 'test/user.json', Scope.GMailSend)

    to_email = open('test/test_email.txt').read().strip()

    await gmail.send(to_email, 'test subject', 'test body')