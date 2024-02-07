# DiceCTF Quals 2024

## Overview

We played with the [O_C_G Team](https://ctftime.org/team/280992) to the DiceCTF Quals 2024. This is the writeup for the challenge "rps-casino", considered as a crypto challenge.

## rps-casino

### Challenge

The challenge is about a rock paper scissor game. The trick is that you have 56 rounds, and you need to win the next 50 rounds in a row to get the flag.

To get the flag, you need to play on the DiceCTF servers, but we have access to the source code to discover how it works, then test and write our scripts.

### How does it works?

The source code of the challenge, written in python, shows that the game isn't really random. A key is generated at the beginning of the game, and each response is generated depending on that key.

In binary, the key looks like this : ``1101001011110001100001100111111111010001100000111011011001001``

