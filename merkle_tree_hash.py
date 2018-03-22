import hashlib
import math


def recursive_mth(array):
    n = len(array)
    if n == 1:
        hash_object = hashlib.sha256(str.encode(str(array[0])))
        hex_dig = hash_object.hexdigest()
        print("ELEMENT: " + str(array[0]) + " - " + hex_dig)
        return hex_dig

    r = math.ceil(math.log(n, 2) - 1)
    k = int(math.pow(2, r))

    init_string = "0x01"

    middle_array = array[0:k]
    middle_string = recursive_mth(middle_array)

    last_array = array[k:n]
    last_string = recursive_mth(last_array)

    full_string = init_string + middle_string + last_string

    print("FULL STRING: " + full_string)

    hash_object = hashlib.sha256(str.encode(full_string))
    hex_dig = hash_object.hexdigest()

    print("HASH: " + hex_dig)
    print("................................................")
    print("")

    return hex_dig


def get_merkle_tree_hash(array):
    if len(array) == 1:
        init_string = "0x00"
        full_string = init_string + str(array[0])
        full_string_bytes = str.encode(full_string)
        hash_object = hashlib.sha256(full_string_bytes)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    else:
        return recursive_mth(array)


def get_array(n):
    array = []
    for i in range(n):
        array.append(i)
    return array


n = int(input("Enter the number of nodes (n): "))
array = get_array(n)

mth = get_merkle_tree_hash(array)

print("-------------------------")
print("FINAL MTH: " + mth)
print("-------------------------")
