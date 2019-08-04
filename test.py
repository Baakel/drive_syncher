def ranges():
    for i in range(100):
        yield i
    print('done')


myranges = ranges()
print(myranges)
for i in myranges:
    print(i*i)