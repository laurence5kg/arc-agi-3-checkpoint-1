with open('main.py', 'r') as f:
    text = f.read()

bad = '''if __name__ == "__main__":
    os.environ["TESTING"] = "False"
    main()'''
good = '''if __name__ == "__main__":
    os.environ["TESTING"] = "False"
    os.environ["OPERATION_MODE"] = "offline"
    main()'''

if bad in text:
    text = text.replace(bad, good)
    with open('main.py', 'w') as f:
        f.write(text)
    print("Patched main.py!")
else:
    print("Could not find block!")
