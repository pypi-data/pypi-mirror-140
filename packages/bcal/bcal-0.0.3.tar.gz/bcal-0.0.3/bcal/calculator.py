def addition(a,b):
    plus = a + b
    print(plus)
def subtraction(a,b):
    minus = a - b
    print(minus)
def multiplication(a,b):
    product = a*b
    print(product)
def division(a,b):
    quotient = a//b
    print(quotient)
def remainder(a,b):
    mod = a%b
    print(mod)
def main():
    a = eval(input())
    b = eval(input())
    while True:

        try:
            user_choice = eval(input())
        except:
            print("please enter a value less than or equal to 5")
        else:
            if(user_choice == 1):
                addition(a,b)
                break
            elif(user_choice == 2):
                subtraction(a,b)
                break
            elif(user_choice == 3):
                multiplication(a,b)
                break
            elif(user_choice == 4):
                division(a,b)
                break
            elif(user_choice == 5):
                remainder(a,b)
                break
if __name__ == "__main__":
    main()