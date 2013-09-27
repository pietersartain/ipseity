import re
import binascii

# Response must be a bytearray
def print_r(response):
  ba_data = str( binascii.hexlify(response) )
  print(re.findall('..?',ba_data))

def print_r_t(response, text):
  print(text)
  print_r(response)

def others():
  pass 
  #tuple = response.to_tuple()
  #ba_tuple = str(binascii.hexlify(bytes(tuple)))

  #print(type(ba_tuple))
  #print(ba_tuple)
  #print(tuple)
  # Split and print by byte
  #print(re.findall('..?',ba_tuple))
