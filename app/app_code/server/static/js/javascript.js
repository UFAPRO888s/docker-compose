// Created by Ethan Chiu 2016
// Updated August 4, 2018

$(document).ready(function () {
  //Pulls info from AJAX call and sends it off to codemirror's update linting
  //Has callback result_cb
  // var socket = io.connect('http://' + document.domain + ':' + location.port + '/check_disconnect');
  var click_count = 0;
  let output_timeout;
  function check_syntax(code, result_cb) {
    //Example error for guideline
    var error_list = [
      {
        line_no: null,
        column_no_start: null,
        column_no_stop: null,
        fragment: null,
        message: null,
        severity: null,
      },
    ];

    //Push and replace errors
    function check(data) {
      //Clear array.
      error_list = [
        {
          line_no: null,
          column_no_start: null,
          column_no_stop: null,
          fragment: null,
          message: null,
          severity: null,
        },
      ];
      document.getElementById("errorslist").innerHTML = "";
      //Check if pylint output is empty.
      if (data == null) {
        result_cb(error_list);
      } else {
        $("#errorslist").append(
          "<tr>" +
            "<th>Line</th>" +
            "<th>Severity</th>" +
            "<th>Error</th>" +
            "<th>Tips</th>" +
            "<th>Error Code</th>" +
            "<th>Error Info</th>" +
            "</tr>"
        );
        var data_length = 0;
        if (data != null) {
          data_length = Object.keys(data).length;
        }
        for (var x = 0; x < data_length; x += 1) {
          if (data[x] == null) {
            continue;
          }
          number = data[x].line;
          code = data[x].code;
          codeinfo = data[x].error_info;
          severity = code[0];
          moreinfo = data[x].message;
          message = data[x].error;

          //Set severity to necessary parameters
          if (severity == "E" || severity == "e") {
            severity = "error";
            severity_color = "red";
          } else if (severity == "W" || severity == "w") {
            severity = "warning";
            severity_color = "yellow";
          }
          //Push to error list
          error_list.push({
            line_no: number,
            column_no_start: null,
            column_no_stop: null,
            fragment: null,
            message: message,
            severity: severity,
          });

          //Get help message for each id
          // var moreinfo = getHelp(id);
          //Append all data to table
          $("#errorslist").append(
            "<tr>" +
              "<td>" +
              number +
              "</td>" +
              '<td style="background-color:' +
              severity_color +
              ';"' +
              ">" +
              severity +
              "</td>" +
              "<td>" +
              message +
              "</td>" +
              "<td>" +
              moreinfo +
              "</td>" +
              "<td>" +
              code +
              "</td>" +
              "<td>" +
              codeinfo +
              "</td>" +
              "</tr>"
          );
        }
        result_cb(error_list);
      }
    }
    //AJAX call to pylint
    // $.post(
    //   "/check_code",
    //   {
    //     text: code,
    //   },
    //   function (data) {
    //     current_text = data;
    //     check(current_text);
    //     return false;
    //   },
    //   "json"
    // );
    const response = fetch("/check_code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ text: code }),
    })
      .then((response) => response.json())
      .then((data) => check(data));
  }
  // var fname =document.getElementById("txt")
  var editor = CodeMirror.fromTextArea(document.getElementById("txt"), {
    mode: {
      name: "python",
      version: 3,
      singleLineStringErrors: false,
    },
    lineNumbers: true,
    indentUnit: 4,
    matchBrackets: true,
    lint: true,
    styleActiveLine: true,
    gutters: ["CodeMirror-lint-markers"],
    lintWith: {
      getAnnotations: CodeMirror.remoteValidator,
      async: true,
      check_cb: check_syntax,
    },
  });
  async function run_code() {
    var fname = document.getElementById("fname").value;
    var code = editor.getValue();
    console.log(fname);
    console.log(code);
    clearTimeout(output_timeout);
    const response = await fetch("/run_code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ text: code }),
    });
    response.json().then((data) => {
      fetch_output(data);
    });
  }
  async function save_code() {
    var fname = document.getElementById("fname").value;
    var code = editor.getValue();
    console.log(fname);
    console.log(code);
    const response = await fetch("/save_code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        filename: fname,
        text: code,
      }),
    });
    response.json().then((data) => {
      print_result(data);
    });
  }
  //Actually Run in Python
  $("#run").click(function () {
    run_code();
  });
  $("#save").click(function () {
    save_code();
  });
  function print_result(data) {
    document.getElementById("output").innerHTML = "";
    $("#output").append("<pre>" + data + "</pre>");
  }
  function fetch_output(ff) {
    let st;
    fetch("/streaming" + ff + ".stdout").then((response) => {
      if (response.ok) {
        response.text().then((str) => {
          print_result(str);
          st = str.trim().split("\n").pop();
          console.log(st);
          if (st === "++++++++++END+++++++++++") {
            clearTimeout(output_timeout);
          }
        });
      }
    });

    output_timeout = setTimeout(function () {
      fetch_output(ff);
    }, 300);
  }
});
