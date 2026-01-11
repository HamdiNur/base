// =====================
// CSRF HELPER
// =====================
function getCSRFToken() {
  return $('input[name="csrf_token"]').val();
}

let usersTable;

$(document).ready(function () {
  // =====================
  // USERS DATATABLE
// =====================
// USERS DATATABLE (only when table exists)
// =====================
if ($("#usersTable").length) {

  usersTable = $("#usersTable").DataTable({
    processing: true,
    serverSide: true,
    pageLength: 10,
      columnDefs: CAN_MANAGE_USERS ? [] : [
    { targets: -1, visible: false, searchable: false }
  ],

    dom:
      '<"row align-items-center mb-3"' +
      '<"col-md-3"l>' +
      '<"user-filters d-flex align-items-center">' +
      '<"col-md-4 ml-auto"f>' +
      '>' +
      'rt' +
      '<"row mt-3"' +
      '<"col-md-5"i>' +
      '<"col-md-7"p>' +
      '>',
    ajax: {
      url: "/user/datatable",
      data: function (d) {
        d.status = $("#statusFilter").val();
        d.role = $("#roleFilter").val();
      }
    },
    drawCallback: function () {
      if (!$.fn.select2 ||
          $("#roleFilter").hasClass("select2-hidden-accessible")) return;
      initFilters();
    }
  });

  $(".user-filters").append($("#userFiltersWrapper").children());
  initFilters();
}


  // =====================
  // INIT TABLE FILTERS
  // =====================
  function initFilters() {
    // STATUS FILTER
    $("#statusFilter")
      .addClass("form-control form-control-sm")
      .off("change")
      .on("change", function () {
        usersTable.ajax.reload();
      });

    // ROLE FILTER (SELECT2 SERVER SIDE)
    $("#roleFilter")
      .off("change")
      .select2({
        width: "resolve",

        placeholder: "All Roles",
        allowClear: true,
        minimumInputLength: 0, // 🔥 IMPORTANT

        ajax: {
          url: "/user/roles/search",
          dataType: "json",
          delay: 250,
          data: function (params) {
            return { q: params.term };
          },
          processResults: function (data) {
            return { results: data };
          },
        },
      })
      .on("change", function () {
        usersTable.ajax.reload();
      });
  }

  // =====================
  // ADD USER MODAL SELECT2
  // =====================
  if ($("#add_user").length) {
    $("#add_user .role-select").select2({
      width: "100%",
      dropdownParent: $("#add_user"),
      ajax: {
        url: "/user/roles/search",
        dataType: "json",
        delay: 250,
        data: function (params) {
          return { q: params.term };
        },
        processResults: function (data) {
          return { results: data };
        },
      },
    });
  }

  // =====================
  // EDIT USER SELECT2
  // =====================
  if ($("#editUserForm").length) {
    $("#editUserForm .role-select").select2({
      width: "100%",
      allowClear: false,
    });
  }

  // =====================
  // ADD USER (AJAX)
  // =====================
  $("#addUserForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr("action"),
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },

    success: function (res) {
        let html = `
    <p><strong>User created successfully.</strong></p>
    <p>
      <strong>Setup Token:</strong><br>
      <code style="font-size:16px">${res.setup_token}</code>
    </p>
    <p>
    The user will use this token to log in once and set their password.
  </p>
    <p class="text-danger">
      ⚠️ Copy this token now. You will NOT see it again.
    </p>
  `;

  Swal.fire({
    title: "User Created",
    html: html,
    icon: "success",
    confirmButtonText: "I have copied it"
  });

  $("#add_user").modal("hide");
  $("#addUserForm")[0].reset();
  usersTable.ajax.reload(null, false);
}
,

      error: function (xhr) {
        Swal.fire(
          "Error",
          xhr.responseJSON?.message || "Something went wrong",
          "error"
        );
      },
    });
  });

  // =====================
  // EDIT USER (AJAX)
  // =====================
  $(document).on("submit", "#editUserForm", function (e) {
    e.preventDefault();

    $.ajax({
      url: this.action,
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },

      success: function (res) {
        Swal.fire({
          icon: "success",
          title: "Updated",
          text: res.message,
        }).then(() => {
          window.location.href = "/user";
        });
      },

      error: function (xhr) {
        Swal.fire(
          "Action blocked",
          xhr.responseJSON?.message || "Update failed",
          "warning"
        );
      },
    });
  });

  // =====================
  // INACTIVE ROLE WARNING
  // =====================
  $(document).on("select2:select", ".role-select", function (e) {
    const text = e.params.data.text || "";

    if (text.includes("(Inactive)")) {
      Swal.fire(
        "Inactive Role",
        "This role is inactive. Please select an active role.",
        "warning"
      );

      $(this).val(null).trigger("change");
    }
  });

  // =====================
  // DELETE USER
  // =====================
  $(document).on("click", ".delete-user", function () {
    const userId = $(this).data("id");

    Swal.fire({
      title: "Are you sure?",
      text: "This user will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: `/user/delete/${userId}`,
        type: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },

        success: function () {
          Swal.fire("Deleted!", "User has been deleted.", "success").then(() =>
            location.reload()
          );
        },

        error: function () {
          Swal.fire("Error!", "Something went wrong.", "error");
        },
      });
    });
  });


  
});
