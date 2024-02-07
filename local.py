import os
from Crypto.Util.number import bytes_to_long

# Just to centralize the names of rps
rockName = 'rock'
paperName = 'paper'
scissorsName = 'scissors'

# For each rps, we have the binary representation
rock = ['0000', '0011', '0110', '1001', '1100', '1111']
paper = ['0001', '0100', '0111', '1010', '1101']
scissors = ['0010', '0101', '1000', '1011', '1110']

# Table of the movements played by the server
tabDone = []

# Original LFSR function from server.py
def LFSR():
    state = bytes_to_long(os.urandom(8))
    while 1:
        yield state & 0xf
        for i in range(4):
            bit = (state ^ (state >> 1) ^ (state >> 3) ^ (state >> 4)) & 1
            state = (state >> 1) | (bit << 63)

rng = LFSR()
n = 56
rps = [rockName, paperName, scissorsName, rockName]

for i in range(n):
    choice = next(rng) % 3

    # We choose to always play rock
    inp = 'rock'
    if inp not in rps:
        print("Invalid choice")
        exit(0)

    # We fill the tabDone table with the responses
    if inp == rps[choice]:
        tabDone.append("rock")
    elif rps.index(inp, 1) - 1 == choice:
        tabDone.append("scissors")
    else:
        tabDone.append("paper")

# Table where we will store the possible keys
tabOfPossibleKeys = []

# As the original key is 64 bits long and a round is 4 bits long, we can play 16 rounds to find the key
for nb in range(16):
    print("Number of round : ", nb)

    # Table of the possibilities of a part of the key, each part is 8 bits long
    # (4 for the nb round, and 4 for the nb+1 round)
    tabKeyPossibilities = []

    # We fill the table with the possibilities of the nb round
    for i in rock if tabDone[nb] == rockName else (paper if tabDone[nb] == paperName else scissors):
        tabKeyPossibilities.append(i)

    # We fill the table with the possibilities of the nb + nb+1 round
    # For example, if the nb round corresponds to rock, and the nb+1 round corresponds to paper
    # We can have the following possibilities: 00010000, 01000000, 01110000, 10100000, 11010000...
    tempTabKeyPossibilities = []
    for i in rock if tabDone[nb + 1] == rockName else (paper if tabDone[nb + 1] == paperName else scissors):
        for j in tabKeyPossibilities.copy():
            tempTabKeyPossibilities.append(i + j)
    tabKeyPossibilities = tempTabKeyPossibilities.copy()

    # For each subkey
    for key in tabKeyPossibilities.copy():
        concat = ''

        # We calculate the xor with the nb and nb+1 round for each subpart of the key
        # The goal here is to find the 4 bits of the nb + 16 round
        # For example, for the first and second round, we are going to create the bits of the 17th round
        # We can then compare our results to the 17th round of the server
        for i in range(4):
            bin1 = key[i:2 + i]
            bin2 = key[3 + i:5 + i]
            xor1 = int(bin1[0]) ^ int(bin1[1])
            xor2 = int(bin2[0]) ^ int(bin2[1])
            res = str(xor1 ^ xor2)
            concat = concat + res

        # If the subkey doesn't allow us to obtain the same result as the server for the nb + 16 round
        # We remove it from the possibilities
        if concat not in (rock if tabDone[nb + 16] == rockName else (paper if tabDone[nb + 16] == paperName else scissors)):
            tabKeyPossibilities.remove(key)

    tabConcat = []
    if nb > 0:
        # For each subkey allowing us to obtain the same result as the server for the nb + 16 round
        # We concatenate it with the previous subkeys
        for key in tabKeyPossibilities:
            for key2 in tabOfPossibleKeys:
                if key[4:] == key2[:4]:
                    tabConcat.append(key[0:4] + key2)
        print("Number of subkeys: ", len(tabConcat))
        tabOfPossibleKeys = tabConcat.copy()
    else:
        # For the first round, we just take the possibilities
        tabOfPossibleKeys = tabKeyPossibilities.copy()

# We remove the first 4 bits of each subkey
for i in range(len(tabOfPossibleKeys)):
    tabOfPossibleKeys[i] = tabOfPossibleKeys[i][4:]

# Function to generate the LFSR using a key
def LFSR_withKey(key):
    state = int(key, 2)
    while 1:
        yield state & 0xf
        for i in range(4):
            bit = (state ^ (state >> 1) ^ (state >> 3) ^ (state >> 4)) & 1
            state = (state >> 1) | (bit << 63)


finalKey = ''
rng_withKey = ''

# For each key in tabOfPossibleKeys, we generate the LFSR and we play 56 times the same moves as the server
# If the moves are the same, we have the key!
for key in tabOfPossibleKeys:
    rng_withKey = LFSR_withKey(key)

    # Table of the movements played by the key
    tabChoice = []
    for i in range(n):
        choice = next(rng_withKey) % 3
        tabChoice.append(rps[choice])

    # If the movements played by the key are the same as the movements played by the server
    # We have the key
    if tabChoice == tabDone:
        finalKey = key
        break

print("finalKey", finalKey)

if finalKey != '':
    # Let's play the 50th next rounds with the key
    for i in range(50):
        choice = next(rng_withKey) % 3
        choiceRobot = next(rng) % 3

        # As we now have the key, we can play the same moves as the server
        # And respond to beat it
        if rps[choice] == rockName:
            print(rps[choiceRobot], paperName)
        elif rps[choice] == paperName:
            print(rps[choiceRobot], scissorsName)
        else:
            print(rps[choiceRobot], rockName)
