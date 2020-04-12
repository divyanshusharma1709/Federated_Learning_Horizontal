package com.airquality.federated;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Environment;
import androidx.appcompat.app.AppCompatActivity;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.ref.Reference;
import java.lang.ref.WeakReference;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.nio.charset.Charset;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import javax.net.ssl.HttpsURLConnection;

import static android.content.ContentValues.TAG;

public class MyAsyncTask extends AsyncTask<URL, Void, String> {


    private String response;
    private final WeakReference<Activity> weakActivity;
    private String mMethod;
    private File file;
    String output;
    public AsyncResponse delegate = null;
    String lineEnd = "\r\n";
    String twoHyphens = "--";
    String boundary = "*****";
    String serverResponseMessage = "";


    MyAsyncTask(Activity activity, File file, String method, AsyncResponse delegate) {
        this.weakActivity = new WeakReference<Activity>(activity);
        this.delegate = delegate;
        this.mMethod = method;
        this.file = file;
    }
    public interface AsyncResponse {
        void processFinish(String output);
    }




    @Override
    protected String doInBackground(URL... strings) {
        String output = null;
        switch (mMethod) {
            case "uploadWeights":
                String response = "";
                try {
                    response = uploadWeights();
                } catch (MalformedURLException e) {
                    e.printStackTrace();
                }
                if (response.equals("OK")) {
                    response = "Upload Successful";
                } else {
                    response = "Upload Failed";
                }
                output = response;
                break;

            case "ismodelUpdated":
                output = isModelUpdated();
                break;
            case "getModel":
                output = downloadFiles();
                break;
            }
            return output;
    }


    private String isModelUpdated() {
        URL url = null;
        try {
            url = new URL("https://fedserveraqi.herokuapp.com/isModelUpdated");
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }

        HttpsURLConnection urlConnection = null;

        try {
            if (url != null) {
                urlConnection = (HttpsURLConnection) url.openConnection();
            }
            if (urlConnection != null) {
                urlConnection.setRequestMethod("GET");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            if (urlConnection != null) {
                urlConnection.connect();
            }
            InputStream in = null;
            if (urlConnection != null) {
                in = new BufferedInputStream(urlConnection.getInputStream());
            }
            response = readStream(in);
            Log.i("Response", response);
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
        }
        return response;
    }

    private String uploadWeights() throws MalformedURLException {
        URL url;
        HttpsURLConnection conn;

        url = new URL("https://fedserveraqi.herokuapp.com/upload");

        try {
            conn = (HttpsURLConnection) url.openConnection();
            conn.setDoOutput(true); // Allow Outputs
            uploadWeight(conn);
            conn.disconnect();

        } catch (IOException e) {
            e.printStackTrace();
        }
        return serverResponseMessage;
    }




    private String readStream(InputStream inputStream) throws IOException {
        StringBuilder output = new StringBuilder();
        if (inputStream != null) {
            InputStreamReader inputStreamReader = new InputStreamReader(inputStream, Charset.forName("UTF-8"));
            BufferedReader reader = new BufferedReader(inputStreamReader);
            java.lang.String line = reader.readLine();
            while (line != null) {
                output.append(line);
                line = reader.readLine();
            }
        }
        return output.toString();
    }


    private byte[] readArrayFromDevice() {
        int size = (int) file.length();
        byte[] bytes = new byte[size];
        try {
            BufferedInputStream buf = new BufferedInputStream(new FileInputStream(file));
            buf.read(bytes, 0, bytes.length);
            buf.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        Log.i("Bytes:", String.valueOf(bytes.length));
        return bytes;
    }

    private String downloadFiles() {
        String response = "Failed";
        HttpURLConnection conn;

        try {
            URL url = new URL("https://fedserveraqi.herokuapp.com/getGlobalModel");
            conn = (HttpsURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            InputStream is = conn.getInputStream();

            DataInputStream dis = new DataInputStream(is);

            byte[] buffer = new byte[1024];
            int length;

            FileOutputStream fos = new FileOutputStream(new File(weakActivity.get().getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), "/checkpoint.zip"));
            while ((length = dis.read(buffer)) > 0) {
                fos.write(buffer, 0, length);
                unzip(weakActivity.get().getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath() + "/checkpoint.zip", weakActivity.get().getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath());
                response = "Download Succeeded";
            }
            int serverResponseCode = conn.getResponseCode();
            String serverResponseMessage = conn.getResponseMessage();
            Log.i("Response Message: ", serverResponseMessage);
            Log.i("Response Code: ", String.valueOf(serverResponseCode));
            dis.close();
            conn.disconnect();
        } catch (MalformedURLException mue) {
            Log.e("Error", mue.getMessage());
        } catch (IOException ioe) {
            Log.e("Error", ioe.getMessage());
        } catch (SecurityException se) {
            Log.e("Error", se.getMessage());
        }
        return response;
    }
    private void uploadWeight(HttpURLConnection conn)
    {
        try {
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("ENCTYPE",
                    "multipart/form-data");
            conn.setRequestProperty("Content-Type",
                    "multipart/form-data;boundary=" + boundary);
            conn.setRequestProperty("file", "weights");

            DataOutputStream dos = new DataOutputStream(conn.getOutputStream());
            dos.writeBytes(twoHyphens + boundary + lineEnd);
            dos.writeBytes("Content-Disposition: form-data; name=\"file\";filename=\""
                    + "weights.bin" + "\"" + lineEnd);

            dos.writeBytes(lineEnd);
            //Write File
            dos.write(readArrayFromDevice());

            dos.writeBytes(lineEnd);
            dos.writeBytes(twoHyphens + boundary + twoHyphens
                    + lineEnd);
            int serverResponseCode = conn.getResponseCode();
            serverResponseMessage = conn.getResponseMessage();
            Log.i("Response Message: ", serverResponseMessage);
            Log.i("Response Code: ", String.valueOf(serverResponseCode));
            dos.flush();
            dos.close();
        } catch (ProtocolException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
        public void unzip(String zipFile, String location) throws IOException {
            try {
                File f = new File(location);
                if (!f.isDirectory()) {
                    f.mkdirs();
                }
                ZipInputStream zin = new ZipInputStream(new FileInputStream(zipFile));
                try {
                    ZipEntry ze = null;
                    while ((ze = zin.getNextEntry()) != null) {
                        String path = location + File.separator + ze.getName();

                        if (ze.isDirectory()) {
                            File unzipFile = new File(path);
                            if (!unzipFile.isDirectory()) {
                                unzipFile.mkdirs();
                            }
                        } else {
                            FileOutputStream fout = new FileOutputStream(path, false);

                            try {
                                for (int c = zin.read(); c != -1; c = zin.read()) {
                                    fout.write(c);
                                }
                                zin.closeEntry();
                            } finally {
                                fout.close();
                            }
                        }
                    }
                } finally {
                    zin.close();
                }
            } catch (Exception e) {
                e.printStackTrace();
                Log.e(TAG, "Unzip exception", e);
            }
        }
    @Override
    protected void onPostExecute(String s) {
        delegate.processFinish(s);
    }
}