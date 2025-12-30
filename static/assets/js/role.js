// ADD ROLE (AJAX)
$("#addRoleForm").on("submit", function (e) {
  e.preventDefault();

  $.ajax({
    url: $(this).attr("action"),
    type: "POST",
    data: $(this).serialize(),

    success: function (res) {
      Swal.fire({
        icon: "success",
        title: "Success",
        text: res.message,
        confirmButtonText: "OK",
      }).then(() => {
        window.location.href = "/roles";
      });
    },

    error: function (xhr) {
      // 👇 HANDLE "ROLE ALREADY EXISTS"
      if (xhr.status === 409) {
        Swal.fire({
          icon: "warning",
          title: "Duplicate Role",
          text: xhr.responseJSON.message,
        });
        return;
      }

      // 👇 GENERAL ERROR
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Something went wrong. Please try again.",
      });
    },
  });
});


$("#editRoleForm").on("submit", function (e) {
  e.preventDefault(); // ⛔ stop normal submit

  $.ajax({
    url: $(this).attr("action"),
    type: "POST",
    data: $(this).serialize(),

    // ✅ UPDATE SUCCESS
    success: function (res) {
      Swal.fire({
        icon: "success",
        title: "Updated",
        text: res.message,
      }).then(() => {
        window.location.href = "/roles";
      });
    },

    // ❌ ERRORS
    error: function (xhr) {

      // 🔁 Duplicate role name
      if (xhr.status === 409) {
        Swal.fire({
          icon: "warning",
          title: "Duplicate Role",
          text: xhr.responseJSON.message,
        });
        return;
      }

      // ❌ Validation / server error
      Swal.fire({
        icon: "error",
        title: "Error",
        text: xhr.responseJSON?.message || "Update failed",
      });
    },
  });
});


$(document).ready(function () {

  // DELETE ROLE
  $(document).on("click", ".delete-role", function () {
    const roleId = $(this).data("id");

    Swal.fire({
      title: "Are you sure?",
      text: "This role will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          url: `/roles/delete/${roleId}`,
          type: "POST",
          success: function (res) {
            Swal.fire(
              "Deleted!",
              res.message || "Role has been deleted.",
              "success"
            ).then(() => location.reload());
          },
          error: function () {
            Swal.fire("Error!", "Something went wrong.", "error");
          },
        });
      }
    });
  });

});


$(document).ready(function () {
  $('#rolesTable').DataTable({
    pageLength: 10
  });
});
