import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.Type;
import java.net.Socket;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

public class TestClient {
    public static ArrayList<SecretKey> byteKeyList = new ArrayList<>();
    public static ArrayList<String> messageInCrumbs = new ArrayList<>();
    public static double packetNumber = 1;


    public static void main(String[] args) {
        try {
            // Connect to the server
            Socket socket = new Socket("localhost", 9999);
            System.out.println("Connected to server.");

            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            DataInputStream in = new DataInputStream(socket.getInputStream());

            //obtains keys from json file
            keyGetter();

            //receives the size of the array from the server
           int amountOfEncryptedPackets = in.readInt();

           //sends the array size to this method to begin decryption process
           messageIteration(amountOfEncryptedPackets, in, out);

           // prints the decrypted message in crumbs
            System.out.println(messageInCrumbs);

            //reconstructs and prints the original message sent by the server
            String originalMessage = combineCrumbsToString(messageInCrumbs);
            System.out.println("Reconstructed Message: " + originalMessage);


        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    //Gets keys from the json file
    private static SecretKey keyGetter() throws IOException {
        Gson gson = new Gson();
        Type type = new TypeToken<HashMap<String, String>>() {
        }.getType();

        try (FileReader reader = new FileReader("aes_keys.json")) {
            // Deserialize the JSON into a HashMap
            HashMap<String, String> keysMap = gson.fromJson(reader, type);

            // Decode hexadecimal strings back to AES SecretKey objects
            byte[] key1 = decodeKey(keysMap.get("00"));
            byte[] key2 = decodeKey(keysMap.get("01"));
            byte[] key3 = decodeKey(keysMap.get("10"));
            byte[] key4 = decodeKey(keysMap.get("11"));

            //Creates SecretKeys for all keys in byte value
            SecretKey secretKey1 = new SecretKeySpec(key1, "AES");
            SecretKey secretKey2 = new SecretKeySpec(key2, "AES");
            SecretKey secretKey3 = new SecretKeySpec(key3, "AES");
            SecretKey secretKey4 = new SecretKeySpec(key4, "AES");

            byteKeyList.add(secretKey1);
            byteKeyList.add(secretKey2);
            byteKeyList.add(secretKey3);
            byteKeyList.add(secretKey4);

            System.out.println("Keys successfully loaded from aes_keys.json");
        }
        return null;
    }

    // changes keys from hex to bytes
    private static byte[] decodeKey(String hex) {
        int length = hex.length();
        byte[] bytes = new byte[length / 2];

        for (int i = 0; i < length; i += 2) {
            bytes[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                    + Character.digit(hex.charAt(i + 1), 16));
        }
        return bytes;
    }

    // decrypts message
    private static String decryptPacket(byte[] encryptedPacket,int numOfPackets, DataOutputStream out) {
        while (true) {
            try {
                // I used the random class as I wasn't sure how to randomize the selection of the key used for decryption
                Random rand = new Random();
                int randomKey = rand.nextInt(4);

                Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
                cipher.init(Cipher.DECRYPT_MODE, byteKeyList.get(randomKey));

                byte[] decrypted = cipher.doFinal(encryptedPacket);
                updateServer(out, numOfPackets);

                return new String(decrypted).trim();
            } catch (IllegalBlockSizeException | BadPaddingException e) {
               System.out.println("Decryption failed with this key. Retrying...");
            } catch (NoSuchPaddingException | NoSuchAlgorithmException | InvalidKeyException e) {
                throw new RuntimeException("Cipher initialization failed", e);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    //Iterates through the array and decrypts a crumb at a time.
    private static void messageIteration(int numOfPackets, DataInputStream in, DataOutputStream out) throws IOException {
        for (int i = 0; i < numOfPackets; i++) {
            byte[] bitPair = new byte[16];
            in.readFully(bitPair);
            String decryptedMessage = decryptPacket(bitPair,numOfPackets, out);
            messageInCrumbs.add(decryptedMessage);
        }
    }
    //This method updates the server with the completion percentage
    private static void updateServer(DataOutputStream out, int numOfPackets) throws IOException {
        double completionFraction = packetNumber / numOfPackets;
        out.writeDouble(completionFraction);
        packetNumber++;
    }

    //Converts the crumbs back into a string
    private static String combineCrumbsToString(ArrayList<String> messageInCrumbs) {
        StringBuilder binaryBuilder = new StringBuilder();

        // Combine all crumbs into a single binary string
        for (String crumb : messageInCrumbs) {
            binaryBuilder.append(crumb);
        }

        String binaryString = binaryBuilder.toString();
        StringBuilder messageBuilder = new StringBuilder();

        // Converts the string of binary to characters (so 8 bits a character)
        for (int i = 0; i < binaryString.length(); i += 8) {
            if (i + 8 <= binaryString.length()) { // Ensure we have a full byte
                String byteStr = binaryString.substring(i, i + 8);
                int charCode = Integer.parseInt(byteStr, 2); // Convert binary to int
                messageBuilder.append((char) charCode); // Convert int to char
            }
        }

        return messageBuilder.toString();
    }
}

