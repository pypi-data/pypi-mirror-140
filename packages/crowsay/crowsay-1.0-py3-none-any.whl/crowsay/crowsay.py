#========================================||
#================PROJECT INFO============||
#========================================||
#==== Auther : SM02 PresenT =============||
#==== Start Date : 10/02/2022 ===========||
#==== End Date : 26/02/2022 =============||
#==== Version : 1.0 BETA ================||
#==== About :  crowSAY Text Output ======||
#==== Note : Do Not Copy My Code , ======||
#==== Otherwise Deleting My project =====||
#========================================||
#================END INFO================||
#========================================||

from os import system
import os , time
import instabot
import optparse

def main():
    parse = optparse.OptionParser()
    parse.add_option("-s","--say",'-S','--say',dest="say",type="string",help="Enter Your Say")
    parse.add_option("-a","-A","--auther","--AUTHER",dest="auther",type="string",help="Specify say FACEBOOK PROFILE URL to get his ID")
    parse.add_option("-u","-U","--update","--UPDATE", dest="update", action="store_true", default=False)
    (options,args) = parse.parse_args()

    say = options.say
    auther = options.auther
    update = options.update
    opt = [say,auther,update]
    if say:
        sm = say
        black='\033[30m'
        blue='\033[44m'
        red='\033[31m'
        print(f"""
        {blue}
           {black} ,_____       /.-----'             
           {black}  '---.\.-.  // ----'              
           {black}   '---<'  `-' .---`__,            
           {black}    `-.`\       .-._,'             
      {red}"{sm}"{black}        `.___.''                   
                        "                       
 """)
    if auther:
        print(f"""
        
░██████╗███╗░░░███╗░█████╗░██████╗░
██╔════╝████╗░████║██╔══██╗╚════██╗
╚█████╗░██╔████╔██║██║░░██║░░███╔═╝
░╚═══██╗██║╚██╔╝██║██║░░██║██╔══╝░░
██████╔╝██║░╚═╝░██║╚█████╔╝███████╗
╚═════╝░╚═╝░░░░░╚═╝░╚════╝░╚══════╝
        """)
        '''print(f"""    
─────────────────────────────────────────────────────────────────────
─██████████████─██████──────────██████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░██████████████░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─██░░░░░░░░░░░░░░░░░░██─██░░██████░░██─██████████░░██─
─██░░██─────────██░░██████░░██████░░██─██░░██──██░░██─────────██░░██─
─██░░██████████─██░░██──██░░██──██░░██─██░░██──██░░██─██████████░░██─
─██░░░░░░░░░░██─██░░██──██░░██──██░░██─██░░██──██░░██─██░░░░░░░░░░██─
─██████████░░██─██░░██──██████──██░░██─██░░██──██░░██─██░░██████████─
─────────██░░██─██░░██──────────██░░██─██░░██──██░░██─██░░██─────────
─██████████░░██─██░░██──────────██░░██─██░░██████░░██─██░░██████████─
─██░░░░░░░░░░██─██░░██──────────██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██████████████─██████──────────██████─██████████████─██████████████─
─────────────────────────────────────────────────────────────────────
        """)'''
        if update:
            print("████████████████████████████████")
            print("█▄─██─▄█▄─▄▄─██▀▄─██─▄─▄─█▄─▄▄─█")
            print("██─██─███─▄▄▄██─▀─████─████─▄█▀█")
            print("▀▀▄▄▄▄▀▀▄▄▄▀▀▀▄▄▀▄▄▀▀▄▄▄▀▀▄▄▄▄▄▀")
            print("\033[31m Checking update .....")
            system('cat .version')
            system(' wget -q https://raw.githubusercontent.com/Simplehacker1Community/Insta-Spam/simplehacker/.ping &> /div/null')
            update = 'truelove'
            file1 = open(".ping", "r")
            readfile = file1.read()
            if update in readfile:
                print("\033[31m Update Found ")
                time.sleep(1)
                print("\033[32m updateing ..")
                system("cd ..")
                system('rm -rf Insta-spam')
                system('git clone htpps://github.com/simplehacker1communty/Insta-spam')
                system('cd Insta-spam')
                system('bash setup.sh')
            else:
                time.sleep(2)
                system('clear')
                auther()
                print("update not found")
                system(f"xdg-open https://t.me/sm02present")
                print("\033[33mPlease visit\n \033[31m https://t.me/sm02present")
        




if  __name__ == "__main__":
    main()
   
