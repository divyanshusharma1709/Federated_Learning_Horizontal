/*
Created by Omid Alemi
Feb 17, 2017
 */

package com.airquality.federated;

import android.os.Environment;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.common.util.ArrayUtils;

import org.tensorflow.Graph;
import org.tensorflow.Session;
import org.tensorflow.Tensor;
import org.tensorflow.Tensors;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.FloatBuffer;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.zip.Deflater;

public class MainActivity extends AppCompatActivity {
    byte[] graphDef;
    Session sess;
    Graph graph;
    File file;
    Tensor<String> checkpointPrefix;
    String checkpointDir;

    static {
        System.loadLibrary("tensorflow_inference");
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        file = new File(getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), "/Weights.bin");
        setContentView(R.layout.activity_main);
        InputStream inputStream;
        try {
            inputStream = getAssets().open("graph.pb");
            byte[] buffer = new byte[inputStream.available()];
            int bytesRead;
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                output.write(buffer, 0, bytesRead);
            }
            graphDef = output.toByteArray();
        } catch (IOException e) {
            e.printStackTrace();
        }
        Graph graph = new Graph();
        sess = new Session(graph);
        graph.importGraphDef(graphDef);
//        inferenceInterface = new TensorFlowInferenceInterface;
//        inferenceInterface.initializeTensorFlow(getAssets(), MODEL_FILE);
        sess.runner().addTarget("init").run();
        Toast.makeText(getApplicationContext(), "Initialized" + sess.toString(), Toast.LENGTH_SHORT).show();
        final TextView W = (TextView) findViewById(R.id.W);
        final TextView B = (TextView) findViewById(R.id.B);
        final Button button = (Button) findViewById(R.id.button);
        final EditText epochs = (EditText) findViewById(R.id.epochs);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                float n_epochs = Float.parseFloat(epochs.getText().toString());
                float num1 = (float) Math.random();
                try (org.tensorflow.Tensor input = Tensor.create(num1);
                     Tensor target = Tensor.create(2*num1 + 3)) {
                    for(int epoch = 0; epoch <= n_epochs; epoch++) {
                        sess.runner().feed("input", input).feed("target", target).addTarget("train").run();
                        ArrayList<Tensor<?>> values = (ArrayList<Tensor<?>>) sess.runner().fetch("W/read").fetch("b/read").run();
                        W.setText((Float.toString(values.get(0).floatValue())));
                        B.setText(Float.toString(values.get(1).floatValue()));
                    }
                }
            }
        });
        Button upload = findViewById(R.id.uploadWeights);
        upload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                MyAsyncTask uploadWeights = new MyAsyncTask(MainActivity.this, file, "uploadWeights", new MyAsyncTask.AsyncResponse() {
                    @Override
                    public void processFinish(String result) {
                        Log.i("Output: uploadWeights", result);
                        Toast.makeText(MainActivity.this, "5 Weights Successfully Uploaded", Toast.LENGTH_SHORT).show();



                    }
                });
                uploadWeights.execute();

                Toast.makeText(MainActivity.this, "5 Weights updated", Toast.LENGTH_SHORT).show();
            }
        });
        Button getModel = findViewById(R.id.getModel);
        getModel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                MyAsyncTask isGlobalModelUpdated = new MyAsyncTask(MainActivity.this, file, "ismodelUpdated", new MyAsyncTask.AsyncResponse() {
                    @Override
                    public void processFinish(String result) {
                        //If True, get Global Model
                            MyAsyncTask getGlobalModel = new MyAsyncTask(MainActivity.this, file, "getModel", new MyAsyncTask.AsyncResponse() {
                                @Override
                                public void processFinish(String result) {
                                    Log.i("Output: GetGlobalModel", result);
                                }
                            });
                            getGlobalModel.execute();
                            Toast.makeText(MainActivity.this, "Fetched Global Model Successfully", Toast.LENGTH_SHORT).show();
                        Log.i("Output: isModelUpdated", "Done");

                    }
                });
                isGlobalModelUpdated.execute();
            }
        });
        //Save Weights in Private Storage
//        finalSave();

        //Upload Weights to Server

        //Check if new model is available



    }

    public void finalSave() {
        ArrayList<ArrayList<Tensor<?>>> at = getWeights();

        ArrayList<float[]> diff = new ArrayList<>();
        ArrayList<ArrayList<Tensor<?>>> bt = getWeights();
        for(int x = 0; x < 4; x++)
        {
            float[] d = new float[flattenedWeight(bt.get(x).get(0)).length];
            float[] bw = flattenedWeight(bt.get(x).get(0));
            float[] aw = flattenedWeight(at.get(x).get(0));

            for(int j = 0; j < bw.length; j++)
            {
                d[j] = aw[j] - bw[j];
            }
            diff.add(d);
        }

        save(diff);
    }

    public ArrayList<ArrayList<Tensor<?>>> getWeights() {
        ArrayList<Tensor<?>> w1 = (ArrayList<Tensor<?>>) sess.runner().fetch("Variable:0").run();
        ArrayList<Tensor<?>> b1 = (ArrayList<Tensor<?>>) sess.runner().fetch("Variable_1:0").run();
        ArrayList<Tensor<?>> w2 = (ArrayList<Tensor<?>>) sess.runner().fetch("Variable_2:0").run();
        ArrayList<Tensor<?>> b2 = (ArrayList<Tensor<?>>) sess.runner().fetch("Variable_3:0").run();
        ArrayList<ArrayList<Tensor<?>>> ls = new ArrayList<>();
        ls.add(w1);
        ls.add(b1);
        ls.add(w2);
        ls.add(b2);
        return ls;
    }

    public void save(ArrayList<float[]> diff){


        int l1 = diff.get(0).length;
        int l2 = diff.get(1).length;
        int l3 = diff.get(2).length;
        int l4 = diff.get(3).length;

        float[] result = new float[l1 + l2 + l3 + l4];
        System.arraycopy(diff.get(0), 0, result, 0, l1);
        System.arraycopy(diff.get(1), 0, result, l1, l2);
        System.arraycopy(diff.get(2), 0, result, l2, l3);
        System.arraycopy(diff.get(3), 0, result, l3, l4);
        saveWeights(result, "Weights.bin");
    }

//    public void logWeight(float[] flat) {
//        String s = "";
//        for (int z = 0; z < flat.length / 10; z++) {
//            s += "  " + flat[z];
//        }
//        Log.i("Array: ", s);
//    }

    public void saveWeights(float[] diff, String name) {
        byte[] byteArray = new byte[diff.length * 4];
        Log.i("Length of FloatArray: ", String.valueOf(diff.length));

        // wrap the byte array to the byte buffer
        ByteBuffer byteBuf = ByteBuffer.wrap(byteArray);

        // create a view of the byte buffer as a float buffer
        FloatBuffer floatBuf = byteBuf.asFloatBuffer();

        // now put the float array to the float buffer,
        // it is actually stored to the byte array
        floatBuf.put(diff);
        saveFile(byteArray, name);
    }

    public void saveFile(byte[] byteArray, String name) {
        File file = new File(getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), name);
        if (!file.exists()) {
            try {
                file.createNewFile();
            } catch (IOException e) {
                Log.i("Error: FILE", "File not Created!");
            }
        }
        OutputStream os = null;
        try {
            os = new FileOutputStream(file);
        } catch (FileNotFoundException e) {
            Log.i("Error: FILE", "File not found!");
        }
        try {
            os.write(byteArray);
            Log.i("FileWriter", "File written successfully");
        } catch (IOException e) {
            Log.i("Error: FILE", "File not written!");
        }
    }

    public void initializeGraph() {
        checkpointPrefix = Tensors.create((getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath() +  "final_model.ckpt").toString());
        checkpointDir = getApplicationContext().getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath();
        graph = new Graph();
        sess = new Session(graph);
        InputStream inputStream;
        try {
            inputStream = getAssets().open("final_graph_hdd.pb");
            byte[] buffer = new byte[inputStream.available()];
            int bytesRead;
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                output.write(buffer, 0, bytesRead);
            }
            graphDef = output.toByteArray();
        } catch (IOException e) {
            e.printStackTrace();
        }
        graph.importGraphDef(graphDef);
        try {
            sess.runner().feed("save/Const", checkpointPrefix).addTarget("save/restore_all").run();
            Toast.makeText(this, "Checkpoint Found and Loaded!", Toast.LENGTH_SHORT).show();
        }
        catch (Exception e) {
            sess.runner().addTarget("init").run();
            Log.i("Checkpoint: ", "Graph Initialized");
        }
    }

    private float[] flattenedWeight(Tensor t) {
        float[] flat = new float[(int) (t.shape()[0]) * (int) t.shape()[1]];
        float[][] arr = new float[(int) (t.shape()[0])][(int) t.shape()[1]];
        t.copyTo(arr);
        int x = 0;
        for (int i = 0; i < t.shape()[0]; i++) {
            for (int j = 0; j < t.shape()[1]; j++) {
                flat[x] = arr[i][j];
                x++;
            }
        }
        return flat;
    }
    private String train(float[][][] features, float[] label, int epochs){
        org.tensorflow.Tensor x_train = Tensor.create(features);
        Tensor y_train = Tensor.create(label);
        int ctr = 0;
        while (ctr < epochs) {
            sess.runner().feed("input", x_train).feed("target", y_train).addTarget("train_op").run();
            ctr++;
        }
        return "Model Trained";
    }
}

