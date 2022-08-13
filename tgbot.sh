#!/usr/bin/bash
#By: Suman Kumar
#Date: 22-oct-2021

#<<<----color code substitution---->>>#
S0="\033[30m" B0="\033[40m"
S1="\033[31m" B1="\033[41m"
S2="\033[32m" B2="\033[42m"
S3="\033[33m" B3="\033[43m"
S4="\033[34m" B4="\033[44m"
S5="\033[35m" B5="\033[45m"
S6="\033[36m" B6="\033[46m"
S7="\033[37m" B7="\033[47m"
R0="\033[00m" R1="\033[0;00m"
#<<<--animation--->>>#
wait() {
  sleep 0.02
}
#<<<---banner---->>>
function banner() {
  printf "${S7}  ╭━━━━╮    ╭╮    ╭╮${R0}\n";wait
  printf "${S6}  ┃╭╮╭╮┃    ┃┃   ╭╯╰╮${R0}\n";wait
  printf "${S3}  ╰╯┃┃┣┻━╮  ┃╰━┳━┻╮╭╯${R0}\n";wait
  printf "${S2}    ┃┃┃╭╮┣━━┫╭╮┃╭╮┃┃${R0}\n";wait
  printf "${S2}    ┃┃┃╰╯┣━━┫╰╯┃╰╯┃╰╮${R0}\n";wait
  printf "${S4}    ╰╯╰━╮┃  ╰━━┻━━┻━╯${R0}\n";wait
  printf "${S1}      ╭━╯┃${R0}\n";wait
  printf "${S1}      ╰━━╯${R0}\n";wait
  printf "${S2}<<${S1}=======${S4}send message from command line${S1}=======${S2}>>${R2}\n";wait
  printf "${S7}Author: ${S4}Suman Kumar ~BHUTUU${R0}\n\n\n";wait
}
#<<<----help menue---->>>#
function HELP() {
  echo -e "
${S2}=====================${R0}
     ${B1}HELP MENUE${R1}
${S2}_____________________${R0}

 ${S2} command                    usage${R0}
 ${S1} =======                    =====${R0}

 ${S4} reset bot${S3}      |-»${S7}   To clear the credential of
                       previous and set new one.${R0}
 ${S4} help${S3}           |-»${S7}   To show this help menue.${R0}

 ${S4} start${S3}          |-»${S7}   To start for sending msges
                       with given bot and chatid${R0}
 ${S4} exit${S3}           |-»${S7}   To EXIT!!${R0}

"
}
#<<<----reset bot----->>>#
function resetbot() {
  if [[ -f "$HOME/.tgbot-config" ]]; then
    new="new"
  else
    new=""
  fi
  printf "${S2}Set your $new BOT TOKEN: ${R0}"
  read newTOKEN
  printf "${S2}Set your $new CHAT_ID: ${R0}"
  read newCHAT_ID
  cat <<-CONF >${HOME}/.tgbot-config
${newTOKEN} ${newCHAT_ID}
CONF
  echo
  if [[ $? == 0 ]]; then
    printf "${S2}[${S4}✔️${S2}]${S6}New configuration successfull${R0}\n"
  else
    printf "${S2}[${S1}❌${S2}]${S1}New configuration failed! Try again!!${R0}\n"
  fi
}
function startbot() {
  while true; do
    if [[ ! -f $HOME/.tgbot-config ]]; then
      printf "${S2}[${S1}!${S2}]${S1} please configure your bot and chat_id!${R0}\n"
      resetbot
    else
      :
    fi
    TOKEN=$(cat $HOME/.tgbot-config | awk '{print $1}')
    CHAT_ID=$(cat $HOME/.tgbot-config | awk '{print $2}')
    printf "${S5}Enter your message: ${R0}"
    read mess
    message=${mess//" "/%20}
    curl "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}?&text=${message}" >/dev/null 2>&1
    if [[ $? == 0 ]]; then
      printf "${S4}Message sent ✔️${R0}\n"
    else
      printf "${S1} message not sent due to any error. check your connection!!${R0}\n"
      echo -e "
${S4}YOUR BOT-TOKEN${S1}::${S7} ${TOKEN}${R0}
${S4}YOUR CHAT_ID${S1}::${S7} ${CHAT_ID}${R0}

${S6}reset it if you foud any error!!${R0}
"
    fi
  done
}
#<<<====Main menue====>>
function main() {
  printf "${S2}Tip${S1}:${S2}: execute '${S4}help${S2}' or '${S4}?${S2}' for help menue\n"
  while true; do
    printf "\033[4;36mTg-bot\033[0;00m \033[1;37m> \033[0;00m"
    read stdinput
    if [[ ${stdinput,,} == 'help' || ${stdinput} == '?' ]]; then
      HELP
    elif [[ ${stdinput,,} == 'reset bot' ]]; then
      resetbot
    elif [[ ${stdinput,,} == 'start' ]]; then
      startbot
    elif [[ ${stdinput,,} == 'banner' ]]; then
      banner
    elif [[ ${stdinput,,} == 'exit' ]]; then
      exit 0
    else
      printf "${S2}[${S1}!${S2}] ${S7}invalid parameter ‘${S4}${stdinput}${S7}’ ${S1}:: ${S7}Execute ‘${S3}help${S7}’ for help menue!!${R0}\n"
    fi
  done
}
banner
main
