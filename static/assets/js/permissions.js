// function getCSRFToken() {
//   return $('input[name="csrf_token"]').val();
// }

// $(document).ready(function () {

//   // ADD PERMISSION
//   $("#addPermissionForm").on("submit", function (e) {
//     e.preventDefault();

//     $.ajax({
//       url: $(this).attr("action"),
//       type: "POST",
//       data: $(this).serialize(),
//       headers: { "X-CSRFToken": getCSRFToken() },

//       success: function (res) {
//         Swal.fire("Success", res.message, "success")
//           .then(() => location.reload());
//       },

//       error: function (xhr) {
//         Swal.fire(
//           "Error",
//           xhr.responseJSON?.message || "Failed",
//           "error"
//         );
//       }
//     });
//   });

//   // PERMISSIONS DATATABLE
//   if ($("#permissionsTable").length) {
//     $("#permissionsTable").DataTable({
//       processing: true,
//       serverSide: true,
//       ajax: "/permissions/datatable",

//       columns: [
//         { data: "id" },
//         { data: "code" },
//         { data: "description" },
//         {
//           data: "is_active",
//           render: d =>
//             d
//               ? '<span class="badge badge-success">Active</span>'
//               : '<span class="badge badge-danger">Inactive</span>'
//         },
//         {
//           data: null,
//           orderable: false,
//           render: row => `
//             <button class="btn btn-sm btn-danger delete-permission"
//                     data-id="${row.id}">
//               Delete
//             </button>
//           `
//         }
//       ]
//     });
//   }

// });


// $(document).ready(function () {

//   $("#rolePermissionsForm").on("submit", function (e) {
//     e.preventDefault();

//     const form = $(this);

//     $.ajax({
//       url: form.attr("action"),
//       method: "POST",
//       data: form.serialize(),
//       success: function (res) {
//         Swal.fire({
//           icon: "success",
//           title: "Saved",
//           text: res.message,
//           timer: 1500,
//           showConfirmButton: false
//         });
//       },
//       error: function (xhr) {
//         Swal.fire({
//           icon: "error",
//           title: "Error",
//           text: xhr.responseJSON?.message || "Something went wrong"
//         });
//       }
//     });
//   });

// });
