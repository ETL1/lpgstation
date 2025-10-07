// "use strict";var KTModalCustomersAdd=function(){var t,e,o,n,r,i;return{init:function(){i=new bootstrap.Modal(document.querySelector("#kt_modal_add_customer")),r=document.querySelector("#kt_modal_add_customer_form"),t=r.querySelector("#kt_modal_add_customer_submit"),e=r.querySelector("#kt_modal_add_customer_cancel"),o=r.querySelector("#kt_modal_add_customer_close"),n=FormValidation.formValidation(r,{fields:{name:{validators:{notEmpty:{message:"Customer name is required"}}},email:{validators:{notEmpty:{message:"Customer email is required"}}},"first-name":{validators:{notEmpty:{message:"First name is required"}}},"last-name":{validators:{notEmpty:{message:"Last name is required"}}},country:{validators:{notEmpty:{message:"Country is required"}}},address1:{validators:{notEmpty:{message:"Address 1 is required"}}},city:{validators:{notEmpty:{message:"City is required"}}},state:{validators:{notEmpty:{message:"State is required"}}},postcode:{validators:{notEmpty:{message:"Postcode is required"}}}},plugins:{trigger:new FormValidation.plugins.Trigger,bootstrap:new FormValidation.plugins.Bootstrap5({rowSelector:".fv-row",eleInvalidClass:"",eleValidClass:""})}}),$(r.querySelector('[name="country"]')).on("change",(function(){n.revalidateField("country")})),t.addEventListener("click",(function(e){e.preventDefault(),n&&n.validate().then((function(e){console.log("validated!"),"Valid"==e?(t.setAttribute("data-kt-indicator","on"),t.disabled=!0,setTimeout((function(){t.removeAttribute("data-kt-indicator"),Swal.fire({text:"Form has been successfully submitted!",icon:"success",buttonsStyling:!1,confirmButtonText:"Ok, got it!",customClass:{confirmButton:"btn btn-primary"}}).then((function(e){e.isConfirmed&&(i.hide(),t.disabled=!1,window.location=r.getAttribute("data-kt-redirect"))}))}),2e3)):Swal.fire({text:"Sorry, looks like there are some errors detected, please try again.",icon:"error",buttonsStyling:!1,confirmButtonText:"Ok, got it!",customClass:{confirmButton:"btn btn-primary"}})}))})),e.addEventListener("click",(function(t){t.preventDefault(),Swal.fire({text:"Are you sure you would like to cancel?",icon:"warning",showCancelButton:!0,buttonsStyling:!1,confirmButtonText:"Yes, cancel it!",cancelButtonText:"No, return",customClass:{confirmButton:"btn btn-primary",cancelButton:"btn btn-active-light"}}).then((function(t){t.value?(r.reset(),i.hide()):"cancel"===t.dismiss&&Swal.fire({text:"Your form has not been cancelled!.",icon:"error",buttonsStyling:!1,confirmButtonText:"Ok, got it!",customClass:{confirmButton:"btn btn-primary"}})}))})),o.addEventListener("click",(function(t){t.preventDefault(),Swal.fire({text:"Are you sure you would like to cancel?",icon:"warning",showCancelButton:!0,buttonsStyling:!1,confirmButtonText:"Yes, cancel it!",cancelButtonText:"No, return",customClass:{confirmButton:"btn btn-primary",cancelButton:"btn btn-active-light"}}).then((function(t){t.value?(r.reset(),i.hide()):"cancel"===t.dismiss&&Swal.fire({text:"Your form has not been cancelled!.",icon:"error",buttonsStyling:!1,confirmButtonText:"Ok, got it!",customClass:{confirmButton:"btn btn-primary"}})}))}))}}}();KTUtil.onDOMContentLoaded((function(){KTModalCustomersAdd.init()}));

"use strict";
var KTModalCylindersAdd = (function () {
  var t, e, o, n, r, i;
  return {
    init: function () {
      (i = new bootstrap.Modal(
        document.querySelector("#kt_modal_add_cylinder")
      )),
        (r = document.querySelector("#kt_modal_add_cylinder_form")),
        (t = r.querySelector("#kt_modal_add_cylinder_submit")),
        (e = r.querySelector("#kt_modal_add_cylinder_cancel")),
        (o = r.querySelector("#kt_modal_add_cylinder_close")),
        (n = FormValidation.formValidation(r, {
          fields: {
            cylinder_size: {
              validators: {
                notEmpty: {
                  message: "Cylinder Type is required",
                },
              },
            },
            qty: {
              validators: {
                notEmpty: {
                  message: "Number of Cylinders is required",
                },
              },
            },
          },
          plugins: {
            trigger: new FormValidation.plugins.Trigger(),
            bootstrap: new FormValidation.plugins.Bootstrap5({
              rowSelector: ".fv-row",
              eleInvalidClass: "",
              eleValidClass: "",
            }),
          },
        })),
        $(r.querySelector('[name="qty"]')).on("change", function () {
          n.revalidateField("qty");
        }),
        t.addEventListener("click", function (e) {
          e.preventDefault(),
            n &&
              n.validate().then(function (e) {
                console.log("validated!"),
                  "Valid" == e
                    ? (t.setAttribute("data-kt-indicator", "on"),
                      (t.disabled = !0),
                      setTimeout(function () {
                        var qty = document.getElementById("qty-value").value;
                        var cylinder_size =
                          document.getElementById("cylinder-size").value;
                        /////////////////////////////////////
                        // $.ajax({
                        //   type: "POST",
                        //   url: "/cylinders/bulk/",
                        //   data: { cylinder_size: cylinder_size, qty: qty },
                        //   success: function (data) {
                        //     // Handle success, e.g., show a message or update UI
                        //     t.removeAttribute("data-kt-indicator"),
                        //       Swal.fire({
                        //         text: "Form has been successfully submitted!",
                        //         icon: "success",
                        //         buttonsStyling: !1,
                        //         confirmButtonText: "Ok, got it!",
                        //         customClass: {
                        //           confirmButton: "btn btn-primary",
                        //         },
                        //       }).then(function (e) {
                        //         e.isConfirmed &&
                        //           (i.hide(),
                        //           (t.disabled = !1),
                        //           (window.location =
                        //             r.getAttribute("data-kt-redirect")));
                        //       });
                        //   },
                        //   error: function (xhr, textStatus, errorThrown) {
                        //     // Handle error
                        //     console.error(
                        //       "Error executing function:",
                        //       errorThrown
                        //     );
                        //   },
                        // });
                        var formData = new FormData();
                        formData.append("cylinder_size", cylinder_size);
                        formData.append("qty", qty);

                        fetch("/cylinders/bulk/", {
                          method: "POST",
                          body: formData,
                          headers: {
                            "X-CSRFToken": csrftoken, // your CSRF token
                          },
                        })
                          .then((resp) => resp.blob())
                          .then((blob) => {
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = "cylinders.pdf";
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                            window.URL.revokeObjectURL(url);
                          });

                        /////////////////////////////////////
                      }, 2e3))
                    : Swal.fire({
                        text: "Sorry, looks like there are some errors detected, please try again.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                          confirmButton: "btn btn-primary",
                        },
                      });
              });
        }),
        e.addEventListener("click", function (t) {
          t.preventDefault(),
            Swal.fire({
              text: "Are you sure you would like to cancel?",
              icon: "warning",
              showCancelButton: !0,
              buttonsStyling: !1,
              confirmButtonText: "Yes, cancel it!",
              cancelButtonText: "No, return",
              customClass: {
                confirmButton: "btn btn-primary",
                cancelButton: "btn btn-active-light",
              },
            }).then(function (t) {
              t.value
                ? (r.reset(), i.hide())
                : "cancel" === t.dismiss &&
                  Swal.fire({
                    text: "Your form has not been cancelled!.",
                    icon: "error",
                    buttonsStyling: !1,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                      confirmButton: "btn btn-primary",
                    },
                  });
            });
        }),
        o.addEventListener("click", function (t) {
          t.preventDefault(),
            Swal.fire({
              text: "Are you sure you would like to cancel?",
              icon: "warning",
              showCancelButton: !0,
              buttonsStyling: !1,
              confirmButtonText: "Yes, cancel it!",
              cancelButtonText: "No, return",
              customClass: {
                confirmButton: "btn btn-primary",
                cancelButton: "btn btn-active-light",
              },
            }).then(function (t) {
              t.value
                ? (r.reset(), i.hide())
                : "cancel" === t.dismiss &&
                  Swal.fire({
                    text: "Your form has not been cancelled!.",
                    icon: "error",
                    buttonsStyling: !1,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                      confirmButton: "btn btn-primary",
                    },
                  });
            });
        });
    },
  };
})();
KTUtil.onDOMContentLoaded(function () {
  KTModalCylindersAdd.init();
});
