import numexpr as ne
import urllib.request
import argparse

def calculates(s, return_float):
    
    ans = ne.evaluate(s)
    
    if return_float:
        ans = float(ans)
    
    return ans

def calculatew(s, return_float):

    s = s.replace(' ','+')
    s = s + '%3F'

    # s
    # http://api.wolframalpha.com/v1/result?
    url = f"http://api.wolframalpha.com/v1/result?input={s}&appid=QVGH4A-ULYGQGK8JW"

    request_url = urllib.request.urlopen(url)

    ans = str(request_url.read(), 'utf-8')  
    ans = ans.replace(' times 10 to the ', 'e')
    
    if return_float:
        if ans.rfind(" ") != -1:
            ans = ans[:ans.rfind(" ")]
        if ans.find(" ") != -1:
            ans = ans[ans.find(" "):]
        ans = float(ans)

    return ans  

def calculate(s, use_Wolfram = False, return_float = False):

    if use_Wolfram:
        ans = calculatew(s, return_float)
    else:
        ans = calculates(s, return_float)

    return ans

def test_1():
    assert abs(4. - calculate('2**2')) < 0.001
    
def test_2():
    assert abs(4. - calculate('2**2')) < 0.001

def test_3():
    assert abs(952. - calculate('34*28')) < 0.001

def test_4():
    assert abs(1. - calculate('sin(pi/2)', use_Wolfram = True, return_float = True)) < 0.001    

def test_5():
    assert abs(1.988435e+30 - calculate('mass of the sun in kg', use_Wolfram = True, return_float = True)) < 0.001e+30

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str)
    parser.add_argument('-w', type=str)
    args = parser.parse_args()
    
#    print('Hello World!')
    
    if args.s != None:
        print(calculates(args.s, return_float=False))
        
    if args.w != None:
        print(calculatew(args.w, return_float=False))