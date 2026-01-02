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
  if ($("#usersTable").length) {
    usersTable = $("#usersTable").DataTable({
      pageLength: 10,
      dom:
        '<"row align-items-center mb-3"' +
        '<"col-md-3"l>' +
        '<"col-md-3"f>' +
        '<"col-md-6 text-right user-filters">' +
        ">" +
        "rt" +
        '<"row mt-3"' +
        '<"col-md-5"i>' +
        '<"col-md-7"p>' +
        ">",
    });

    $(".user-filters").html($("#userFiltersWrapper").html());
  }

  // =====================
  // STATUS FILTER (EXACT MATCH)
  // =====================
  $(document).on("change", "#statusFilter", function () {
    const value = this.value;

    if (value) {
      usersTable
        .column(5) // Status column
        .search("^" + value + "$", true, false)
        .draw();
    } else {
      usersTable.column(5).search("").draw();
    }
  });

  // =====================
  // ROLE FILTER (EXACT MATCH)
  // =====================
  $(document).on("change", "#roleFilter", function () {
    const value = this.value;

    if (value) {
      usersTable
        .column(4) // Role column
        .search("^" + value + "$", true, false)
        .draw();
    } else {
      usersTable.column(4).search("").draw();
    }
  });

  // =====================
  // SELECT2 ROLE DROPDOWN
  // =====================
  // $('.role-select').select2({
  //   dropdownParent: $('#add_user'),
  //   placeholder: 'Select role',
  //   allowClear: true,
  //   ajax: {
  //     url: '/user/roles/search',
  //     dataType: 'json',
  //     delay: 250,
  //     data: function (params) {
  //       return { q: params.term };
  //     },
  //     processResults: function (data) {
  //       return { results: data };
  //     }
  //   }
  // });
  if ($("#add_user").length) {
    $("#add_user .role-select").select2({
      dropdownParent: $("#add_user"),
      placeholder: "Select role",
      allowClear: true,
      ajax: {
        url: "/user/roles/search",
        dataType: "json",
        delay: 250,
        data: (params) => ({ q: params.term }),
        processResults: (data) => ({ results: data }),
      },
    });
  }

  // EDIT USER SELECT2 (NORMAL PAGE)
  if ($("#editUserForm").length) {
    $("#editUserForm .role-select").select2({
      width: "100%",
      placeholder: "Select role",
      allowClear: false,
    });
  }

  // =====================
  // ADD USER
  // =====================
  $("#addUserForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr("action"),
      type: "POST",
      data: $(this).serialize(),
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      success: function (res) {
        Swal.fire("Success", res.message, "success").then(() =>
          location.reload()
        );
      },
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
  // EDIT USER
  // EDIT USER (AJAX ONLY)
  // =====================
  $(document).on("submit", "#editUserForm", function (e) {
  e.preventDefault(); // ⛔ stop normal submit

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
        confirmButtonText: "OK"
      }).then(() => {
        // ✅ redirect AFTER user confirms
        window.location.href = "/user";
      });
    },

    error: function (xhr) {
      Swal.fire({
        icon: "warning",
        title: "Action blocked",
        text: xhr.responseJSON?.message || "Update failed",
      });
    },
  });
});


  // INACTIVE ROLE WARNING (SELECT2 SAFE)
  // =====================
  $(document).on("select2:select", ".role-select", function (e) {
    const text = e.params.data.text || "";

    if (text.includes("(Inactive)")) {
      Swal.fire({
        icon: "warning",
        title: "Inactive Role",
        text: "This role is inactive. Please select an active role.",
      });

      $(this).val(null).trigger("change");
    }
  });

  //
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
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: `/user/delete/${userId}`,
        type: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
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
