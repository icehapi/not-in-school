import random
import string

def generate():
    code = ""
    verifyCode = ""
    cnt = 0
    s = string.ascii_letters
    for i in range(1, 33):
        rand = random.randint(0,1)
        if(cnt <= 16):
            if(rand == 0):
                temp = random.randint(0, 9)
                code += str(temp)
                verifyCode += str((temp + i) % 10)
                cnt += 1
            elif(rand == 1):
                temp = random.choice(s)
                code += temp
                if(temp.islower()):
                    verifyCode += chr((ord(temp) - ord('a') + i) % 26 + ord('a'))
                else:
                    verifyCode += chr((ord(temp) - ord('A') + i) % 26 + ord('A'))
        else:
            temp = random.choice(s)
            code += temp
            if(temp.islower()):
                verifyCode += chr((ord(temp) - ord('a') + i) % 26 + ord('a'))
            else:
                verifyCode += chr((ord(temp) - ord('A') + i) % 26 + ord('A'))
    return code, verifyCode

print("生成uploadCode...")
code, verifyCode = generate()
print("Client_Code: " + code)
print("Server_Code: " + verifyCode)
print("生成updateCode...")
code, verifyCode = generate()
print("Client_Code: " + code)
print("Server_Code: " + verifyCode)
        