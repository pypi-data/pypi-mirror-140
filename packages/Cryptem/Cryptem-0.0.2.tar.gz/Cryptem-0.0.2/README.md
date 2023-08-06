An easy-to-use object-oriented API for working with cryptography: encrypting/decrypting data and files as well as signing data and verifying signatures.  
Can be used for asymmetric and symmetric cryptography, signature verification, and supports password-like private keys.
Uses elliptic curve cryptography for the data encryption and data signing, the file encryption however uses AES.  
Built on the eciespy, cryptography, coincurve and hashlib modules.

## Classes `Crypt` and `Encryptor`:
The `Crypt` class is a cryptographic tool used by the holder of a private key for encrypting and signing data. It's counterpart is the `Encryptor` class, which using a specific public key can ecrypt data and verify signatures.  
These classes also include functionality for more efficient file encryption using AES secret keys, where the secret key is automatically asymmetrically encrypted and embedded in the symmetrically encrypted file. This means that the usage of this file encryption system is asymmetric (private & public key), although the encryption of the file itself is not.   
Can be used for single-session asymmetric (public-key/private-key) cryptography
as well as for (optionally password secured) multi-session (i.e. reused keys) asymmetric (public-key/private-key) or symetric (private-key-only) cryptography.  
__Single-session__ means the keys are used only as long as the Crypt instance exists, so when the program is restarted different keys are used.  
__Multi-session__ means that the same keys can be reused after restarting the program, a simplified form of the private key must be memorised by the user as a password (although you can of course use a longer key-like string instead of a typical password).

# Encryption
## Usage:
`from Cryptem import Crypt`
### - __Single-Session Asymetric Encryption__ (public-key and private-key):
Communication Receiver:
  
    crypt = Crypt() # create Crypt object with new random public and private keys
    public_key = crypt.public_key # read public key

  Give `public_key` (the public key) to Sender (the code in the program below).

Communication Sender/Encryptor:
  
    # Object-Oriented Approach:
    from Cryptem import Encryptor
    encryptor = Encryptor(public_key)  # crete Encryptor object with Receiver's public key
    cipher = encryptor.Encrypt("Hello there!".encode('utf-8')) # encrypt a message
    
    # Functional Approach:
    cipher = Encrypt("Hello there!".encode('utf-8'), public_key)

  Transmit `cipher` to Receiver.

Communication Receiver:
  
    # continued from above
    plaintext = crypt.Decrypt(cipher).decode('utf-8') # decrypt message

### - __Multi-Session Asymetric Encryption__ (public-key and private-key):  
Communication Receiver:
    
    crypt = Crypt("mypassword")   # create Crypt object with a password, from which private and ublic keys are generated
    public_key = crypt.public_key # read public key
      
Give `public_key` to Sender.

Communication Sender/Encryptor:
    
    encryptor = Encryptor(public_key)  # crete Encryptor object with Receiver's public key
    cipher = encryptor.Encrypt("Hello there!".encode('utf-8')) # encrypt a message

Transmit `cipher` to Receiver.

Communication Receiver/Decryptor:

    # continued from above
    plaintext = crypt.Decrypt(cipher).decode('utf-8') # decrypt message


###  - __Multi-Session Symmetric Enryption__ (private-key only):  
  Sender/Encryptor:
  
      crypt = Crypt("our_password")
      cipher = crypt.Encrypt("Hello there!".encode('utf-8'))
  
  SECURELY & PRIVATELY transmit the password to the Receiver (this is the downside and weakness of symmetric encryption).
  
  Transmit `cipher` to other Receiver.
  
  Receiver:
  
      # continued from aboveplaintext
      crypt = Crypt("our_password")
      plaintext = crypt.Decrypt(cipher).decode('utf-8')
## File Encryption:
Because the encryption technologies used above are rather inefficient when applied to larger quantities of data, the Crypt and Encryptor classes have fcuntions that implement symmetric AES encryption. The secret AES key is encrypted with asymmetric elliptic curve cryptography (exactly as the encryption methods above) and embedded into the file, so that the API user (programmer) need not worry about it, and can use the file encryption functionality in exactly the same way as the bytearray-encryption function above.

Sender/Encryptor:

    crypt = Crypt() # create Crypt object with new random public and private keys
    public_key = crypt.public_key # read public key

  Give `public_key` (the public key) to Sender (the code in the program below).

  Communication Sender/Encryptor:

    # Object-Oriented Approach:
    encryptor = Encryptor(public_key)  # crete Encryptor object with Receiver's public key
    encryptor.EncryptFile("/path/to/file", "/where/to/save/encrypted/file") # encrypt a file

    # Functional Approach:
    EncryptFile("/path/to/file", "/where/to/save/encrypted/file", public_key)

  Transmit the encrypted file to Receiver.

  Communication Receiver:

    # continued from above
    plaintext = crypt.DecryptFile("/path/to/encrypted/file", "/path/to/decrypted/file") # decrypt file

# Signing
CURRENTLY SEEMS TO BE BROKEN, ERROR SOURCE IN THE UNDERLYING COINCURVE MODULE  
Digital cryptographic signing data means creating a signature from and for a piece of data using a certain private key (in this case a password). Anybody can verify that the signature was indeed created using the private key by using the corresponding public key.

  Sender/Signer:
  
    data = "hello there!".encode("utf-8")
    
    crypt = Crypt("my_password")  # create a Crypt object using a password
    public_key = crypt.public_key # this is the public key you should share with others
    signature = crypt.Sign(data)  # creating a signature for data
    
  Transmit `data`, `public_key` and `signature` to Receiver/Verifier.
  
  Receiver/Verifier:
  
    encryptor = Encryptor(public_key)
    assert(encryptor.VerifySignature(data, signature)) # checking the validity of data's signature using the signer's public key
    
    
    