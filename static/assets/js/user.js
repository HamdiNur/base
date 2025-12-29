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

  // ADD USER (AJAX)
  $("#addUserForm").on("submit", function (e) {
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
        }).then(() => location.reload());
      },
      error: function (xhr) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: xhr.responseJSON.message,
        });
      },
    });
  });

});
