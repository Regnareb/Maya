import timeit

s = """
def patterniser(file_name, ratio, final_size=[]):
    from PIL import Image
    pattern_image = Image.open(file_name, 'r')
    pattern_width, pattern_height = pattern_image.size
    final_width = int(ratio * pattern_width)
    final_height = int(ratio * pattern_height)
    result_image = Image.new('RGB', (final_width, final_height))
    for x in xrange(int(ratio) + 1):
        coordX = pattern_width * x
        coordY = final_height
        for y in xrange(int(ratio) + 2):
            result_image.paste(pattern_image, (coordX, coordY))
            coordY -= pattern_height
    if final_size:
        result_image = result_image.resize((final_size[0], final_size[1]), Image.ANTIALIAS)
    return result_image


def patterniser2(file_name, ratio, final_size=[]):
    from PIL import Image
    pattern_image = Image.open(file_name, 'r')
    final_width, final_height = pattern_image.size
    rat = int(final_width/ratio)
    pattern_image = pattern_image.resize((rat, rat), Image.ANTIALIAS)
    pattern_width, pattern_height = pattern_image.size
    result_image = Image.new('RGB', (final_width, final_height))
    
    for x in xrange(int(ratio) + 1):
        coordX = pattern_width * x
        coordY = final_height
        for y in xrange(int(ratio) + 2):
            result_image.paste(pattern_image, (coordX, coordY))
            coordY -= pattern_height
    if final_size:
        result_image = result_image.resize((final_size[0], final_size[1]), Image.ANTIALIAS)
    return result_image

DUMMY
""" 
n = 10
for i in xrange(1, 10):
    i = i*0.5
    #for u in [512, 1024, 2048, 4096, 8192]:
    for u in [1024]:
        print '%s - %s*%s' % (i, u, u)
        exec1 = "patterniser('/tmp/placeholder.png', %s, [%s, %s])" % (i, u, u)
        exec2 = "patterniser2('/tmp/placeholder.png', %s, [%s, %s])" % (i, u, u)
        print timeit.timeit(s.replace('DUMMY', exec1), number=n)
        print timeit.timeit(s.replace('DUMMY', exec2), number=n)
        print "\n"
    print "\n"
