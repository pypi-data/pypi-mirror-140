
def Fibonacci(n):
    if n < 0:
        print("Incorrect input")

    elif n == 0:
        return 0
 
    elif n == 1 or n == 2:
        return 1
 
    else:
        return Fibonacci(n-1) + Fibonacci(n-2)

def fibSequence(n):
    a = 0
    b = 1
    if n == 1:
        print(a)
    else:
        print(a , end = ' ')
        print(b , end = ' ')
        for i in range(2,n):
            c = a + b
            a = b
            b = c
            print(c,end =' ')

def isPalindrome(x) :
    s = str(x)
    i = 0
    j = len(s) - 1
    while (i < j) :
        if (s[i] != s[j]) :
            return False
        else :
            i += 1
            j -= 1
    return True

def isPangram(sentence):
    ABCD = "abcdefghijklmnopqrstuvwxyz"
    for alphabet in ABCD:
        if alphabet not in sentence:
            return False

    return True

def countVowel(sentence):
    vowels = "aeiou"
    count = 0

    for letter in vowels:
        count += sentence.count(letter)

    return count

def isIsogram(string):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    for letter in alphabet:
        if string.lower().count(letter) > 1:
            return False
    return True

def getMiddle(s):
    length = int(len(s)/2)
    if len(s)%2 == 0: return(s[length-1: length+1]) 

    return(s[length:length+1])

def removeVowel(string_):
    vowels = ["a","e","i","o","u", "A" , "E", "I", "O", "U"]
    
    '''Check if any letter from the array is in the string then remove it'''
    for letter in vowels:
        if letter in string_:
            string_ = string_.replace(letter,"")
            
    return string_

def romanToInt(s) :
    sum = 0
    arr = list(s)
    i = 0
    while (i < len(arr)) :
        if (arr[i]=='I'):
            if (i + 1 == len(arr)):
                sum = sum + 1
            elif(arr[i + 1] == 'V'):
                sum = sum + 4
                i = i + 1
            elif(arr[i + 1] == 'X') :
                sum = sum + 9
                i = i + 1
            else:
                sum = sum + 1
        elif(arr[i]=='V'):
                sum = sum + 5
        elif(arr[i]=='X'):
            if (i + 1 == len(arr)) :
                sum = sum + 10
            elif(arr[i + 1] == 'L') :
                sum = sum + 40
                i = i + 1
            elif(arr[i + 1] == 'C') :
                sum = sum + 90
                i = i + 1
            else :
                sum = sum + 10
        elif(arr[i]=='L'):
                sum = sum + 50
        elif(arr[i]=='C'):
            if (i + 1 == len(arr)) :
                sum = sum + 100
            elif(arr[i + 1] == 'D') :
                sum = sum + 400
                i = i + 1
            elif(arr[i + 1] == 'M') :
                sum = sum + 900
                i = i + 1
            else :
                sum = sum + 100
        elif(arr[i]=='D'):
                sum = sum + 500
        elif(arr[i]=='M'):
                sum = sum + 1000
        i += 1
    return sum