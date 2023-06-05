const configuration = {
  container: document.getElementById("blockmirror-editor"),
};
let editor = new BlockMirror(configuration);
if (loadcode_url != "") {
  var client = new XMLHttpRequest();
  client.open("GET", loadcode_url);
  client.onreadystatechange = function () {
    //   alert(client.responseText);
    editor.setCode(client.responseText);
    check_syntax();
  };
  client.send();
}
function print_result(data) {
  document.getElementById("output").innerHTML = "<pre>" + data + "</pre>";
}
async function run_code() {
  const response = await fetch("/run_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ text: editor.getCode() }),
  });
  response.json().then((data) => {
    // print_result(data);
    fetch_output(data);
  });
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
  const output_img_url="/streaming/tmp/output.jpg"
  fetch(output_img_url).then((response) => {
    if (response.ok) {
      document.getElementById("output_img").setAttribute("src", output_img_url);
    }
  });
  output_timeout = setTimeout(function () {
    fetch_output(ff);
  }, 500);
}

async function save_code() {
  var fname = document.getElementById("fname").value;
  console.log(fname);
  const response = await fetch("/save_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      filename: fname,
      text: editor.getCode(),
    }),
  });
  response.json().then((data) => {
    print_result(data);
  });
}
var code_checked = 0;
function result_cb(error_list) {
  var found = [];

  for (var i in error_list) {
    var error = error_list[i];

    // Null check to make sure eror message is not empty
    if (
      error.line_no != null &&
      error.message != null &&
      error.severity != null
    ) {
      var start_line = error.line_no;

      var start_char;
      if (typeof error.column_no_start != "undefined")
        start_char = error.column_no_start;
      else start_char = error.column_no;

      var end_char;

      if (typeof error.column_no_stop != "undefined")
        end_char = error.column_no_stop;
      else end_char = error.column_no;

      var end_line = error.line_no;
      var message = error.message;

      var severity;
      if (typeof error.severity != "undefined") {
        severity = error.severity;
      } else {
        severity = "error";
      }

      found.push({
        from: CodeMirror.Pos(start_line - 1, start_char),
        to: CodeMirror.Pos(end_line - 1, end_char),
        message: message,
        severity: severity, // "error", "warning"
      });
    }
  }

  updateLinting(cm, found);
}
async function check_syntax() {
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
    // document.getElementById("errorslist").innerHTML = "";
    var html_table = "";
    //Check if pylint output is empty.
    var data_length = 0;
    if (data != null) {
      data_length = Object.keys(data).length;
    }
    if (data_length == 0) {
      // result_cb(error_list);
    } else {
      html_table +=
        "<tr>" +
        "<th>Line</th>" +
        "<th>Severity</th>" +
        "<th>Error</th>" +
        "<th>Tips</th>" +
        "<th>Error Code</th>" +
        "<th>Error Info</th>" +
        "</tr>";

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

        // Get help message for each id
        // var moreinfo = getHelp(id);
        // Append all data to table
        html_table +=
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
          "</tr>";
      }
      document.getElementById("errorslist").innerHTML = html_table;
      // result_cb(error_list);
    }
    return error_list;
  }

  const response = await fetch("/check_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ text: editor.getCode() }),
    // body: { code: editor.getCode() },
  });
  response.json().then((data) => {
    // print_result(data);
    code_checked = check(data);
  });

  // response.json().then(data =>{print_result(data);});
  checkcode_timeout = setTimeout(function () {
    check_syntax();
  }, 5000);
}

// setInterval(check_syntax, 10000);
