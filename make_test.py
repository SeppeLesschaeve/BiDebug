from operator import mod


if __name__ == "__main__":
    amount = 1000
    f = open("proef_statement.py",mode="w+")
    f.truncate(0)
    f.write("def f():\n\tpass\n")
    for i in range(amount):
        f.write("f()\n")
    f.close()
    f = open("infile.txt",mode="w+")
    f.truncate(0)
    for i in range(amount):
        f.write("1\n")
    for i in range(amount):
        f.write("2\n")
    f.write("3\n")
    f.close()