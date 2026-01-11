// =====================
// CSRF + PAGE DATA
// =====================
const projectData = document.getElementById("projectData");

const MANAGERS_URL = projectData?.dataset.managersUrl;
const ASSIGN_MANAGER_URL = projectData?.dataset.assignManagerUrl;
const CSRF_TOKEN = projectData?.dataset.csrfToken;

function getCSRFToken() {
  return CSRF_TOKEN || document.querySelector('input[name="csrf_token"]')?.value || "";
}

let projectsTable;

$(document).ready(function () {

  // =====================
  // PROJECTS DATATABLE
  // =====================
  if ($("#projectsTable").length) {
    projectsTable = $("#projectsTable").DataTable({
      processing: true,
      serverSide: true,
      ajax: {
        url: "/projects/datatable",
        type: "GET"
      },
      columns: [
        {
          data: "name",
        
        },
        { data: "manager" },
        {
          data: "members",
          render: data => `${data} member${data !== 1 ? "s" : ""}`
        },
        {
          data: "is_active",
          render: data =>
            data
              ? '<span class="badge badge-success">Active</span>'
              : '<span class="badge badge-danger">Inactive</span>'
        },
        { data: "created_at" },
        {
          data: "id",
          orderable: false,
          searchable: false,
          className: "text-right",
          render: id => `
            <div class="dropdown dropdown-action">
              <a href="#" class="action-icon dropdown-toggle" data-toggle="dropdown">
                <i class="material-icons">more_vert</i>
              </a>
              <div class="dropdown-menu dropdown-menu-right">
                <a class="dropdown-item" href="/projects/${id}">
                  <i class="fa fa-eye"></i> View
                </a>
                <a class="dropdown-item" href="/projects/edit/${id}">
                  <i class="fa fa-pencil"></i> Edit
                </a>
                <button class="dropdown-item text-danger delete-project" data-id="${id}">
                  <i class="fa fa-trash-o"></i> Delete
                </button>
              </div>
            </div>
          `
        }
      ]
    });
  }

  // =====================
  // ADD PROJECT
  // =====================
  $("#addProjectForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: "/projects/add",
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },
      success: res => {
        Swal.fire("Success", res.message, "success").then(() => {
          window.location.href = `/projects/${res.project_id}`;
        });
      },
      error: xhr => {
        Swal.fire("Error", xhr.responseJSON?.message || "Failed to create project", "error");
      }
    });
  });

  // =====================
  // EDIT PROJECT
  // =====================
  $("#editProjectForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      headers: { "X-CSRFToken": getCSRFToken() },
      success: res => {
        Swal.fire("Updated", res.message, "success").then(() => {
          window.location.href = "/projects";
        });
      },
      error: xhr => {
        Swal.fire("Error", xhr.responseJSON?.message || "Failed to update project", "error");
      }
    });
  });

  // =====================
  // DELETE PROJECT
  // =====================
  $(document).on("click", ".delete-project", function () {
    const projectId = $(this).data("id");

    Swal.fire({
      title: "Are you sure?",
      text: "This project will be permanently deleted!",
      icon: "warning",
      showCancelButton: true
    }).then(result => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: `/projects/delete/${projectId}`,
        type: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        success: res => {
          Swal.fire("Deleted", res.message, "success");
          projectsTable?.ajax.reload(null, false);
        },
        error: xhr => {
          Swal.fire("Error", xhr.responseJSON?.message || "Cannot delete project", "error");
        }
      });
    });
  });

  // =====================
  // SELECT2 – MANAGERS
  // =====================
  if ($("#managerSelect").length && MANAGERS_URL) {
    $("#managerSelect").select2({
      dropdownParent: $("#assignManagerModal"),
      placeholder: "Select manager",
      allowClear: true,
      width: "100%",
      ajax: {
        url: MANAGERS_URL,
        dataType: "json",
        delay: 250,
        data: params => ({ q: params.term }),
        processResults: data => data
      }
    });
  }

  // =====================
  // ASSIGN MANAGER
  // =====================
  $("#saveManagerBtn").on("click", function () {
    const managerId = $("#managerSelect").val();

    if (!managerId) {
      Swal.fire("Error", "Please select a manager", "error");
      return;
    }

    $.ajax({
      url: ASSIGN_MANAGER_URL,
      type: "POST",
      headers: { "X-CSRFToken": getCSRFToken() },
      data: { manager_id: managerId },
      success: res => {
        $("#assignManagerModal").modal("hide");
        Swal.fire("Success", res.message, "success").then(() => location.reload());
      },
      error: xhr => {
        Swal.fire("Error", xhr.responseJSON?.message || "Something went wrong", "error");
      }
    });
  });

  // =====================
  // MEMBERS SELECT2
  // =====================
  const membersUrl = projectData?.dataset.membersUrl;
  const addMemberUrl = projectData?.dataset.addMemberUrl;
  const removeMemberUrl = projectData?.dataset.removeMemberUrl;

  if ($("#memberSelect").length && membersUrl) {
    $("#memberSelect").select2({
      placeholder: "Select user",
      width: "100%",
      ajax: {
        url: membersUrl,
        dataType: "json",
        delay: 250,
        data: params => ({ q: params.term }),
        processResults: data => data
      }
    });
  }
  $("#unassignManagerBtn").on("click", function () {
  const data = $("#projectData");

  Swal.fire({
    title: "Unassign manager?",
    text: "This will remove the manager from the project.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Unassign"
  }).then((result) => {
    if (!result.isConfirmed) return;

    $.ajax({
      url: `/projects/${data.data("project-id")}/unassign-manager`,
      type: "POST",
      headers: {
        "X-CSRFToken": data.data("csrf-token")
      },
      success: function (res) {
        Swal.fire("Success", res.message, "success")
          .then(() => location.reload());
      },
      error: function (xhr) {
        Swal.fire(
          "Error",
          xhr.responseJSON?.message || "Failed to unassign manager",
          "error"
        );
      }
    });
  });
});


  // =====================
  // ADD MEMBER
  // =====================
  $("#saveMemberBtn").on("click", function () {
    const userId = $("#memberSelect").val();
    if (!userId) return;

    $.ajax({
      url: addMemberUrl,
      type: "POST",
      headers: { "X-CSRFToken": getCSRFToken() },
      data: { user_id: userId },
      success: () => location.reload(),
      error: xhr => alert(xhr.responseJSON?.message || "Error")
    });
  });

  // =====================
  // REMOVE MEMBER
  // =====================
  $(document).on("click", ".remove-member", function () {
    const userId = $(this).data("user-id");

    Swal.fire({
      title: "Remove member?",
      text: "This user will be removed from the project.",
      icon: "warning",
      showCancelButton: true
    }).then(result => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: removeMemberUrl,
        type: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: { user_id: userId },
        success: res => {
          Swal.fire("Removed!", res.message || "Member removed", "success")
            .then(() => location.reload());
        },
        error: xhr => {
          Swal.fire("Error", xhr.responseJSON?.message || "Failed", "error");
        }
      });
    });
  });

}); // ✅ END DOCUMENT READY
