import sys
import getopt

def main(*args, **kwargs):
    opts, args = getopt.getopt(args, "cb:k", ["mx", "take="])
    try:
        bear_name = None
        is_mx = False
        for op, value in opts:
            if op == "-c":
                print("cccc")
            elif op == "-b":
                bear_name = value
                print(bear_name)
        try:
            arg = args[0]
        except:
            arg = None
        try:
            arg_value = args[1]
        except:
            arg_value = None
        if arg == "mx":
            is_mx = True
            if not arg_value:
                raise Exception("must have mx value")
        if is_mx:
            print(f"mx success haha {arg_value}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    args = sys.argv[1:]
    main(*args)
