#!/bin/bash

python3 -m coverage run ../server.py 8080 &
coverage_PID=$!
sleep 1


# Checking the REGISTER and LOGIN commands work
python3 registerlogin.py > registerlogin.txt
DIFF=$(diff registerlogin.txt registerlogin.out)
if [ "$DIFF" == "" ]
then
    registerlogin="Passed"
else
    registerlogin="Failed"
fi
sleep 0.2

# Checking the CREATE and JOIN commands work
python3 createjoin.py > createjoin.txt
DIFF=$(diff createjoin.txt createjoin.out)
if [ "$DIFF" == "" ]
then
    createjoin="Passed"
else
    createjoin="Failed"
fi
sleep 0.2

# Checking the REGISTER command after user has logged in
python3 registerafterlogin.py > registerafterlogin.txt
DIFF=$(diff registerafterlogin.txt registerafterlogin.out)
if [ "$DIFF" == "" ]
then
    registerafterlogin="Passed"
else
    registerafterlogin="Failed"
fi
sleep 0.2

# Checking the CREATE and JOIN commands work for multiple channels
python3 createjoinmultiple.py > createjoinmultiple.txt
DIFF=$(diff createjoinmultiple.txt createjoinmultiple.out)
if [ "$DIFF" == "" ]
then
    createjoinmultiple="Passed"
else
    createjoinmultiple="Failed"
fi
sleep 0.2

# Checking the SAY command works
python3 say.py > say.txt
DIFF=$(diff say.txt say.out)
if [ "$DIFF" == "" ]
then
    say="Passed"
else
    say="Failed"
fi
sleep 0.2

# Checking the CHANNELS command works
python3 channels.py > channels.txt
DIFF=$(diff channels.txt channels.out)
if [ "$DIFF" == "" ]
then
    channels="Passed"
else
    channels="Failed"
fi
sleep 0.2

# If a user tries some commands without logging in
python3 notloggedin.py > notloggedin.txt
DIFF=$(diff notloggedin.txt notloggedin.out)
if [ "$DIFF" == "" ]
then
    notloggedin="Passed"
else
    notloggedin="Failed"
fi
sleep 0.2

# If an invalid command is given
python3 invalidcommand.py > invalidcommand.txt
DIFF=$(diff invalidcommand.txt invalidcommand.out)
if [ "$DIFF" == "" ]
then
    invalidcommand="Passed"
else
    invalidcommand="Failed"
fi
sleep 0.2

# Checking when each command does not have enough parameters
python3 wronglength.py > wronglength.txt
DIFF=$(diff wronglength.txt wronglength.out)
if [ "$DIFF" == "" ]
then
    wronglength="Passed"
else
    wronglength="Failed"
fi
sleep 0.2

# Checking when a username already exists for the REGISTER command
python3 usernametaken.py > usernametaken.txt
DIFF=$(diff usernametaken.txt usernametaken.out)
if [ "$DIFF" == "" ]
then
    usernametaken="Passed"
else
    usernametaken="Failed"
fi
sleep 0.2

# Checking when the given username has not been registered or the password is wrong
python3 wronguserdetails.py > wronguserdetails.txt
DIFF=$(diff wronguserdetails.txt wronguserdetails.out)
if [ "$DIFF" == "" ]
then
    wronguserdetails="Passed"
else
    wronguserdetails="Failed"
fi
sleep 0.2

# Checking when a client leaves and another client uses their vacated login
python3 loggedout1.py > loggedout1.txt
sleep 0.2
python3 loggedout2.py > loggedout2.txt
DIFF=$(diff loggedout2.txt loggedout2.out)
if [ "$DIFF" == "" ]
then
    loggedout="Passed"
else
    loggedout="Failed"
fi
sleep 0.2

# Checking when a client tries to login twice
python3 logintwice.py > logintwice.txt
DIFF=$(diff logintwice.txt logintwice.out)
if [ "$DIFF" == "" ]
then
    logintwice="Passed"
else
    logintwice="Failed"
fi
sleep 0.2

# Checking when a user tries to join a channel that has not been created
python3 joinnochannel.py > joinnochannel.txt
DIFF=$(diff joinnochannel.txt joinnochannel.out)
if [ "$DIFF" == "" ]
then
    joinnochannel="Passed"
else
    joinnochannel="Failed"
fi
sleep 0.2

# Checking when a user tries to join the same channel twice
python3 jointwice.py > jointwice.txt
DIFF=$(diff jointwice.txt jointwice.out)
if [ "$DIFF" == "" ]
then
    jointwice="Passed"
else
    jointwice="Failed"
fi
sleep 0.2

# Checking when a user tries to create the same channel twice
python3 createalreadyexists.py > createalreadyexists.txt
DIFF=$(diff createalreadyexists.txt createalreadyexists.out)
if [ "$DIFF" == "" ]
then
    createalreadyexists="Passed"
else
    createalreadyexists="Failed"
fi
sleep 0.2

# Checking when a user tries to send a message to a channel they haven't joined
python3 notinchannel.py > notinchannel.txt
DIFF=$(diff notinchannel.txt notinchannel.out)
if [ "$DIFF" == "" ]
then
    notinchannel="Passed"
else
    notinchannel="Failed"
fi
sleep 0.2

# Checking when a user tries to send a message to a channel that doesn't exist
python3 channeldoesntexist.py > channeldoesntexist.txt
DIFF=$(diff channeldoesntexist.txt channeldoesntexist.out)
if [ "$DIFF" == "" ]
then
    channeldoesntexist="Passed"
else
    channeldoesntexist="Failed"
fi

kill -2 $coverage_PID > /dev/null
sleep 1
echo ""
echo "Coverage:"
python3 -m coverage report ../server.py

echo ""
echo "Test cases:"

echo '[{"registerlogin": "'$registerlogin'"}, {"createjoin": "'$createjoin'"},
{"registerafterlogin": "'$registerafterlogin'"},
{"createjoinmultiple": "'$createjoinmultiple'"}, {"say": "'$say'"},
{"channels": "'$channels'"}, {"notloggedin": "'$notloggedin'"},
{"invalidcommand": "'$invalidcommand'"}, {"wronglength": "'$wronglength'"},
{"usernametaken": "'$usernametaken'"},
{"wronguserdetails": "'$wronguserdetails'"}, {"loggedout": "'$loggedout'"},
{"logintwice": "'$logintwice'"}, {"joinnochannel": "'$joinnochannel'"},
{"jointwice": "'$jointwice'"},
{"createalreadyexists": "'$createalreadyexists'"},
{"notinchannel": "'$notinchannel'"},
{"channeldoesntexist": "'$channeldoesntexist'"}]' | jq -c
echo ""
