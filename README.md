
The goal of this project is to implement the "Quantum Crypto" polarized light algorithm.

Using either Java, Python, or C#, create an implementation of the algorithm which transmits data from a server to a client.  The server will load a file from disk and transmit it to the client two bits at a time, with each pair of bits encoded as either horizontally, vertically, clockwise, or counterclockwise polarized light.  The server should create a standard payload (say, "The quick brown fox jumps over the lazy dog.") which is transmitted in each packet.  The encoding of the bits of the message will actually be contained within the encryption key used for the message and not the plaintext itself.

To simulate the polarization of light and the destructive nature of the algorithm, for each packet the server generates it uses AES and one of four keys that it shares with the client to encrypt the payload.  The server selects which packet to use for encryption based on the bit pair.  The client initially randomly selects one of the keys and attempts to decrypt the packet.

If the packet decrypts correctly (the payload contains the readable phrase) then the client converts the selected encryption key back to the corresponding bit pair.  Otherwise, the client discards the packet and marks that key as invalid for that packet.

The file's contents are transmitted as packets representing bit pairs in order, and the client replies with the fraction 0%-100% which it has currently decoded.  While the client's completion is below 100%, the server continues to re-send the packets in order using the same algorithm.

You are allowed to use built-in security libraries for your language of choice in order to handle the AES encrypt and decrypt operations.
