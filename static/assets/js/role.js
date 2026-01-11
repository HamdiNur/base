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
  let msg = "Unexpected error";

  if (xhr.responseJSON && xhr.responseJSON.message) {
    msg = xhr.responseJSON.message;
  } else if (xhr.status === 401) {
    msg = "You are not logged in";
  } else if (xhr.status === 403) {
    msg = "You do not have permission to delete this role";
  } else if (xhr.status === 409) {
    msg = "Role is in use and cannot be deleted";
  }

  Swal.fire("Error", msg, "error");
}
,
      });
    });
  });

  // =====================
  // DATATABLE
 // =====================
// ROLES DATATABLE (SERVER SIDE)
// =====================
let rolesTable;

if ($("#rolesTable").length) {
  rolesTable = $("#rolesTable").DataTable({
    processing: true,
    serverSide: true,
    pageLength: 10,

    dom:
      '<"row align-items-center mb-3"' +
        '<"col-md-4"l>' +
        '<"col-md-4 text-center"f>' +
        '<"col-md-4 text-right">' +
      ">" +
      "rt" +
      '<"row mt-3"' +
        '<"col-md-5"i>' +
        '<"col-md-7"p>' +
      ">",

    ajax: {
      url: "/roles/datatable",
      type: "GET"
    },

  columns: [
  { data: "name" },
  { data: "code" },
  { data: "description" },
  {
    data: "is_active",
    render: function (data) {
      return data
        ? '<span class="badge badge-success">Active</span>'
        : '<span class="badge badge-danger">Inactive</span>';
    }
  },
{
  data: null,   // ✅ THIS IS REQUIRED
  orderable: false,
  searchable: false,
  className: "text-right",
  render: function (data, type, row) {
    return `
      <div class="dropdown dropdown-action">
        <a href="#" class="action-icon dropdown-toggle" data-toggle="dropdown">
          <i class="material-icons">more_vert</i>
        </a>
        <div class="dropdown-menu dropdown-menu-right">
          <a class="dropdown-item" href="/roles/edit/${row.id}">
            <i class="fa fa-pencil m-r-5"></i> Edit
          </a>
          <button
            type="button"
            class="dropdown-item text-danger delete-role"
            data-id="${row.id}">
            <i class="fa fa-trash-o m-r-5"></i> Delete
          </button>
        </div>
      </div>
    `;
  }
}


]

  });
}


  
});
