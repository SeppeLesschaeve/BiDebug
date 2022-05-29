from operator import mod


if __name__ == "__main__":
    amount = 500
    f = open("proef_statement.py",mode="w+")
    f.truncate(0)
    f.write("i = 1\n")
    for i in range(amount):
        f.write("while i == 1:\n\ti -= 1\nwhile i == 0:\n\ti += 1\n")
    f.close()
    f = open("infile.txt",mode="w+")
    f.truncate(0)
    for i in range(amount):
        f.write("1\n")
    for i in range(amount):
        f.write("2\n")
    f.write("3\n")
    f.close()