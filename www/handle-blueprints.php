<?php
// Read/write blueprints for the experiment

/*
 * The backend is expected to have the following architecture:
 * ./blueprints
 *      2020-06-01_blueprint_###.json
 *      ...
 *      used_2020-06-01_blueprint_###.json
 *      ...
 *
 * Where ### is the md5 hash of the blueprint contents.
 * When blueprints have been used they will have their filename changed to indicate this.
 */

include('blueprint-config.php');
$path = "./blueprints/";
$data_array = json_decode(file_get_contents('php://input'), true);

if($data_array) {
    // Save incoming blueprints for requests with data
    // Expected structure of $data_array:
    // $data_array = {
    //  password: string,
    //  blueprint: string (JSON)
    // }

    // Check authorisation
    if(!array_key_exists("password", $data_array) ||
        $data_array["password"] != BLUEPRINT_PASSWORD) {
        // Incorrect password!
        http_response_code(401);
        die();
    }

    // Save blueprint
    if(array_key_exists("blueprint", $data_array)) {
        $content = json_encode($data_array["blueprint"]);
        $hash = md5($content);
        $filename = date('Y-m-d') . '_blueprint_' . $hash . '.json';
        // Check whether file exists already
        if(file_exists($path . $filename) ||
            file_exists($path. 'used_' . $filename)) {
            // File already exists!
            http_response_code(422);
            die();
        }

        file_put_contents($path . $filename, $content);
    }

} else {
    // Return a blueprint to empty requests

    // Identify a candidate blueprint
    // List all candidate blueprints
    // First check unused blueprints
    $all_files = scandir($path);
    $all_files = preg_grep("/\.json$/i", $all_files);
    $unused_files = array();
    foreach($all_files as $f) {
        if(!preg_match("/^used_/", $f))
            array_push($unused_files, $f);
    }
    $filename = "";
    $content = "";

    if(sizeof($unused_files) > 0) {
        shuffle($unused_files);
        $filename = array_pop($unused_files);
        $content = file_get_contents($path . $filename);

//        The Surrey server has permission issues renaming files so we don't do that here anymore
        // Mark blueprint as used
//        $save_as = 'used_' . $filename;
//        if(file_put_contents($path . $save_as, $content) === false) {
//            // Could not update filename to mark as used!
//            http_response_code(500);
//            die();
//        } else {
//            unlink($path . $filename);
//        }
    } elseif (sizeof($all_files) > 0) {
        shuffle($all_files);
        $filename = array_pop($all_files);
        $content = file_get_contents($path . $filename);
    } else {
        // Could not find any blueprints!
        http_response_code(503);
        die();
    }

    // Send blueprint back
    // The expected response will be a JSON with the following content:
    // {
    //  blueprint_id: string,
    //  blueprint: string (JSON)
    // }
    $out = array(
        "blueprint_id" => $filename,
        "blueprint" => json_decode($content)
    );

    echo json_encode($out);
}