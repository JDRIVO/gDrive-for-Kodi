import sys, os
import encryption

saltFile = sys.argv[1]
password = sys.argv[2]
filePath = sys.argv[3]
destinationPath = sys.argv[4]

encrypt = encryption.encryption(saltFile, password)

fileName = os.path.basename(filePath)
fileName = encrypt.decryptString(fileName)

destinationPath = os.path.join(destinationPath, fileName)
encrypt.decryptFile(filePath, destinationPath)