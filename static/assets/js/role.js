function getCSRFToken() {
  return $('input[name="csrf_token"]').val();
}

$(document).ready(function () {
  // =====================
  // ADD ROLE
  // =====================
  $("#addRoleForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr("action"),
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },

      success: function (res) {
        Swal.fire("Success", res.message, "success").then(
          () => (window.location.href = "/roles")
        );
      },

      error: function (xhr) {
        if (xhr.status === 409) {
          Swal.fire("Duplicate Role", xhr.responseJSON.message, "warning");
          return;
        }

        Swal.fire(
          "Error",
          xhr.responseJSON?.message || "Something went wrong",
          "error"
        );
      },
    });
  });

  // =====================
  // EDIT ROLE
  // =====================
  $("#editRoleForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr("action"),
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },

      success: function (res) {
        Swal.fire("Updated", res.message, "success").then(
          () => (window.location.href = "/roles")
        );
      },

      error: function (xhr) {
        if (xhr.status === 409) {
          Swal.fire("Duplicate Role", xhr.responseJSON.message, "warning");
          return;
        }

        Swal.fire(
          "Error",
          xhr.responseJSON?.message || "Update failed",
          "error"
        );
      },
    });
  });

  // =====================
  // DELETE ROLE
  // =====================
  $(document).on("click", ".delete-role", function () {
    const roleId = $(this).data("id");

    Swal.fire({
      title: "Are you sure?",
      text: "This role will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
    }).then((result) => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: `/roles/delete/${roleId}`,
        type: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },

        success: function (res) {
          Swal.fire("Deleted", res.message, "success").then(() =>
            location.reload()
          );
        },

        error: function (xhr) {
          Swal.fire(
            "Error",
            xhr.responseJSON?.message || "Cannot delete role",
            "error"
          );
        },
      });
    });
  });

  // =====================
  // DATATABLE
  // =====================
  let rolesTable;

  $(document).ready(function () {
    rolesTable = $("#rolesTable").DataTable({
      pageLength: 10,
      dom:
        '<"row align-items-center mb-3"' +
        '<"col-md-4"l>' +
        '<"col-md-4 text-center"f>' +
        '<"col-md-4 text-right status-filter-container">' +
        ">" +
        "rt" +
        '<"row mt-3"' +
        '<"col-md-5"i>' +
        '<"col-md-7"p>' +
        ">",
    });

    // Move status filter into toolbar
    $(".status-filter-container").html($("#statusFilterWrapper").html());

    // Status filter logic (exact match)
    $(document).on("change", "#statusFilter", function () {
      const value = this.value;

      if (value) {
        rolesTable
          .column(3)
          .search("^" + value + "$", true, false)
          .draw();
      } else {
        rolesTable.column(3).search("").draw();
      }
    });
  });
});
