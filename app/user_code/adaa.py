<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />

    <link rel="shortcut icon" href="/static/img/favicon.ico" />
    <link rel="stylesheet" href="/static/css/style.css" />
    <link rel="stylesheet" href="/static/css/hover-min.css" />
    <link rel="stylesheet" href="/static/css/bootstrap.min.css" />

    <title>File explorer</title>
  </head>

  <body>
    <nav
      class="navbar navbar-expand-lg navbar-dark"
      style="background-color: #aaaaaa"
    >
      <a class="navbar-brand hvr-shadow" href="/explorer/"
        ><img src="/static/img/Robolab.svg" style="width: 50px; position: top"
      /></a>

      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item">
            <a class="nav-link" href="/explorer">File</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/controller">Controller</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/lesson">Lesson</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/help">Help</a>
          </li>
        </ul>
        <ul class="navbar-nav ml-auto mt-2 mb-2">
          <div id="upload-form-container" style="display: none">
            <div class="md-form" id="uploadForm" style="display: none">
              <input
                style="color: white"
                class="btn btn-sm"
                type="file"
                multiple
                name="files[]"
                id="file1"
                onchange="uploadFile(_('file1').files)"
              />
              <p>
                <progress
                  id="progressBar"
                  value="0"
                  max="100"
                  style="width: 100px"
                ></progress>
              </p>
              <p id="status"></p>
              <p id="loaded_n_total"></p>
            </div>
            <!-- </div> -->
            <button
              id="uploadButton"
              class="btn btn-sm mr-4 ml-4"
              style="margin-bottom: 6px; margin-top: 3px"
            >
              Upload
            </button>
          </div>

          <button class="btn btn-light mr-1" id="view0_button" >
            <i class="fas fa-th-large"></i>
            icons
          </button>
          <button class="btn btn-light mr-3" id="view1_button" >
            <i class="fas fa-list"></i>
            details
          </button>
        </ul>
      </div>
    </nav>

    <div class="container">
      <div class="row">
        <div
          class="col-12 lead mt-4"
          style="text-align: left; margin-bottom: -10px"
        >
            <hr />
        </div>
      </div>
    </div>



<div class="container">
        <div class="row">
            <div class="col-md-12">
                <div style="padding:100px 15px; text-align:center;">
                    <h1>
                        <strong></strong></h1>
                    <h3 class='text-muted'>
                        Page not found!</h3>
                    <div class="error-details lead">
                        Sorry, an error has occured, Requested page not found!
                    </div>
                    <div style = "margin-top:15px; margin-bottom:15px;">
                        <a href="/" class="btn btn-info btn-lg" >
                            Take Me Home </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    





    <script src="/static/js/jquery-3.2.1.slim.min.js"></script>
    <script src="/static/js/popper.min.js"></script>
    <script src="/static/js/bootstrap.min.js"></script>

    <script>
      $("#uploadButton").click(function () {
        document.getElementById("uploadForm").style.display = "block";
        document.getElementById("uploadButton").style.display = "none";
      });
    </script>

    <script>
      let timeout;
      $(function () {
        $('[data-toggle="tooltip"]').tooltip();
      });

      $(function () {
        $("#view0_button").click(function () {
          $("#view1_container").css("display", "none");
          $("#view0_container").css("display", "block");
          $("#view0_button").prop("disabled", true);
          $("#view1_button").prop("disabled", false);

          const Http = new XMLHttpRequest();
          const url = "/changeView?view=0";
          Http.open("GET", url);
          Http.send();
        });
        $("#view1_button").click(function () {
          $("#view0_container").css("display", "none");
          $("#view1_container").css("display", "block");
          $("#view1_button").prop("disabled", true);
          $("#view0_button").prop("disabled", false);

          const Http = new XMLHttpRequest();
          const url = "/changeView?view=1";
          Http.open("GET", url);
          Http.send();
        });
      });
      function _(el) {
        return document.getElementById(el);
      }
      function humanFileSize(bytes, si = false, dp = 1) {
        const thresh = si ? 1000 : 1024;

        if (Math.abs(bytes) < thresh) {
          return bytes + " B";
        }

        const units = si
          ? ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
          : ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"];
        let u = -1;
        const r = 10 ** dp;

        do {
          bytes /= thresh;
          ++u;
        } while (
          Math.round(Math.abs(bytes) * r) / r >= thresh &&
          u < units.length - 1
        );

        return bytes.toFixed(dp) + " " + units[u];
      }

      function uploadFile(file) {
        // var file = _("file1").files;
        // alert(file.name+" | "+file.size+" | "+file.type);
        document.getElementById("uploadForm").style.display = "block";
        document.getElementById("uploadButton").style.display = "none";
        var formdata = new FormData();
        _("progressBar").value = 0;
        for (let i = 0; i < file.length; i++) {
          formdata.append("files", file[i]);
        }
        // formdata.append("files", file);
        var ajax = new XMLHttpRequest();
        ajax.upload.addEventListener("progress", progressHandler, false);
        ajax.addEventListener("load", completeHandler, false);
        ajax.addEventListener("error", errorHandler, false);
        ajax.addEventListener("abort", abortHandler, false);
        ajax.open("POST", "/upload");
        ajax.send(formdata);
      }

      function progressHandler(event) {
        _("loaded_n_total").innerHTML =
          "Uploaded " +
          humanFileSize(event.loaded) +
          " of " +
          humanFileSize(event.total);
        var percent = (event.loaded / event.total) * 100;
        _("progressBar").value = Math.round(percent);
        _("status").innerHTML =
          Math.round(percent) + "% uploaded... please wait";
      }

      function completeHandler(event) {
        const obj = JSON.parse(event.target.responseText);
        alert(obj.message);
        document.getElementById("uploadForm").style.display = "none";
        document.getElementById("uploadButton").style.display = "block";
        timeout = setTimeout(update_page, 500);
        // _("status").innerHTML = obj.message;
        // _("progressBar").value = 0; //wil clear progress bar after successful upload
      }

      function errorHandler(event) {
        // _("status").innerHTML = "Upload Failed";
        alert("Upload Failed");
        timeout = setTimeout(update_page, 500);
      }

      function abortHandler(event) {
        // _("status").innerHTML = "Upload Aborted";
        alert("Upload Aborted");
        timeout = setTimeout(update_page, 500);
      }
    </script>
  </body>
</html>