import com.google.gson.Gson;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.io.FileWriter;
import java.util.HashMap;
/*
this class will generate and store the keys used for crypto functions into a json file
 */
public class KeyGeneration {
    public static void main(String[] args) throws Exception {

        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(128); // 128-bit AES keys
        SecretKey key1 = keyGen.generateKey(); // For bit pair 00
        SecretKey key2 = keyGen.generateKey(); // For bit pair 01
        SecretKey key3 = keyGen.generateKey(); // For bit pair 10
        SecretKey key4 = keyGen.generateKey(); // For bit pair 11

        String hexKey = bytesToHex(key1.getEncoded());
        String hexKey2 = bytesToHex(key2.getEncoded());
        String hexKey3 = bytesToHex(key3.getEncoded());
        String hexKey4 = bytesToHex(key4.getEncoded());

        System.out.println("AES Key in Hex: " + hexKey);
        System.out.println("AES Key in Hex2: " + hexKey2);
        System.out.println("AES Key in Hex3: " + hexKey3);
        System.out.println("AES Key in Hex4: " + hexKey4);

        HashMap<String, String> keysMap = new HashMap<>();
        keysMap.put("00", bytesToHex(key1.getEncoded()));
        keysMap.put("01", bytesToHex(key2.getEncoded()));
        keysMap.put("10", bytesToHex(key3.getEncoded()));
        keysMap.put("11", bytesToHex(key4.getEncoded()));

        // Serialize the keys map to JSON using Gson
        Gson gson = new Gson();
        String jsonKeys = gson.toJson(keysMap);

        // writes to json file
        try (FileWriter writer = new FileWriter("aes_keys.json")) {
            writer.write(jsonKeys);
        }

        System.out.println("Keys have been generated and stored in aes_keys.json");

    }
    public static String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            hexString.append(String.format("%02x", b));
        }
        return hexString.toString();
    }
}
