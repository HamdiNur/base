$(function () {

  /* ===============================
     ROLE SELECT (Select2)
  =============================== */
  const $roleSelect = $("#roleSelect");
  if ($roleSelect.length) {
    const $roleData = $("#roleData");
    const currentRoleId = $roleData.data("role-id");
    const currentRoleName = $roleData.data("role-name");

    $roleSelect.select2({
      placeholder: "Select role",
      width: "100%",
      ajax: {
        url: "/roles/select2",
        dataType: "json",
        delay: 250,
        data: params => ({ q: params.term || "" }),
        processResults: data => ({ results: data.results })
      }
    });

    if (currentRoleId && currentRoleName) {
      const option = new Option(currentRoleName, currentRoleId, true, true);
      $roleSelect.append(option).trigger("change");
    }

    $roleSelect.on("select2:select", e => {
      window.location.href = `/roles/${e.params.data.id}/permissions`;
    });
  }

  /* ===============================
     ASSIGN PERMISSIONS (AJAX)
  =============================== */
  const $form = $("form[action*='/permissions']");
  if (!$form.length) return;

  $form.on("submit", function (e) {
    e.preventDefault(); // 🔥 THIS WAS MISSING

    $.ajax({
      url: $form.attr("action"),
      type: "POST",
      data: $form.serialize(),
      success: function (res) {
        Swal.fire({
          icon: "success",
          title: "Saved",
          text: res.message || "Permissions updated successfully",
          timer: 1500,
          showConfirmButton: false
        });
      },
      error: function (xhr) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: xhr.responseJSON?.message || "Something went wrong"
        });
      }
    });
  });

});
