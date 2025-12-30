$(document).ready(function () {

  // DELETE USER
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
      if (result.isConfirmed) {
        $.ajax({
          url: `/user/delete/${userId}`,
          type: "POST",
          success: function () {
            Swal.fire("Deleted!", "User has been deleted.", "success")
              .then(() => location.reload());
          },
          error: function () {
            Swal.fire("Error!", "Something went wrong.", "error");
          },
        });
      }
    });
  });
  $("#editUserForm").on("submit", function (e) {
  e.preventDefault(); // ⛔ stop normal submit

  $.ajax({
    url: $(this).attr("action"),
    type: "POST",
    data: $(this).serialize(),

    // ✅ SUCCESS
    success: function (res) {
      Swal.fire({
        icon: "success",
        title: "Updated",
        text: res.message,
      }).then(() => {
        window.location.href = "/user";
      });
    },

    // ❌ ERRORS
    error: function (xhr) {

      // 🔁 Duplicate username/email
      if (xhr.status === 409) {
        Swal.fire({
          icon: "warning",
          title: "Duplicate User",
          text: xhr.responseJSON.message,
        });
        return;
      }

      Swal.fire({
        icon: "error",
        title: "Error",
        text: xhr.responseJSON?.message || "Update failed",
      });
    },
  });
});


  let usersTable;

$(document).ready(function () {

  // USERS TABLE
  if ($('#usersTable').length) {
    usersTable = $('#usersTable').DataTable({
      pageLength: 10,
      processing: true
    });
  }
// STATUS FILTER (column index 5)
  $('#statusFilter').on('change', function () {
    usersTable.column(5).search(this.value).draw();
  });

  // ROLE FILTER (column index 4)
  $('#roleFilter').on('change', function () {
    usersTable.column(4).search(this.value).draw();
  });
  // SELECT2
  $('.role-select').select2({
    dropdownParent: $('#add_user'),
    placeholder: 'Select role',
    allowClear: true,
    ajax: {
      url: '/user/roles/search',
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return { q: params.term };
      },
      processResults: function (data) {
        return { results: data };
      }
    }
  });

  // ADD USER
  $('#addUserForm').on('submit', function (e) {
    e.preventDefault();
    $.ajax({
      url: $(this).attr('action'),
      type: 'POST',
      data: $(this).serialize(),
      success: function (res) {
        Swal.fire('Success', res.message, 'success')
          .then(() => location.reload());
      },
      error: function (xhr) {
        Swal.fire(
          'Error',
          xhr.responseJSON?.message || 'Something went wrong',
          'error'
        );
      }
    });
  });

});

$('#refreshUsers').on('click', function () {
  usersTable.draw(false);   // 👈 HERE
});


});
