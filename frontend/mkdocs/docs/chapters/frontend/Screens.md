## Screens

Below, all implemented screens of the Post-Covid Challenge Frontend can be seen. Two roles are provided: maintainers and users. Each screen is designed for a specific role, which is explicitly mentioned in the respective sections below.

### Home

The starting point of the Post-Covid Challenge is the Home screen. Users can see a overview of available studies and data provided by the system. The can also create an new or sign into their existing account.

[![Home](../../media/frontend/screens/Home_NotLoggedIn.png 'Home')](../../media/frontend/screens/Home_NotLoggedIn.png 'Home')

_Home screen_

---

### Registration

On the registration screen, users enter their personal data, role, planned functionality, and a valid e-mail address and password. They must also confirm the terms of use and privacy policy in order to complete registration. After completing registration, the user receives a confirmation email to the provided email address. If the user is already registered, they can go directly to the login area.

[![Registration](../../media/frontend/screens/Registration.png 'Registration')](../../media/frontend/screens/Registration.png 'Registration')

_Registration screen_

---

### Login

On the login screen, the user can log in with their access data and optionally remain logged in. It is also possible to reset the password. If there is no account, the user is redirected to the registration page.

[![Login](../../media/frontend/screens/Login.png 'Login')](../../media/frontend/screens/Login.png 'Login')

_Login screen_

---

### Forgot Password

On the Forgot Password screen, users can request a password reset link to regain access to their account.

[![ForgotPassword](../../media/frontend/screens/Home_ForgotPassword.png 'ForgotPassword')](../../media/frontend/screens/Home_ForgotPassword.png 'ForgotPassword')

_Forgot Password screen_

---

### Password Reset

On the Password Reset screen, users can enter a new password after receiving a reset link, allowing them to recover access to their account.

[![PasswordReset](../../media/frontend/screens/PasswordReset.png 'PasswordReset')](../../media/frontend/screens/PasswordReset.png 'PasswordReset')

_Password Reset screen_

---

### Home (Logged In)

On the Home screen (logged in), users can access all available functions that were selected during registration.

[![Home](../../media/frontend/screens/Home.png 'Home')](../../media/frontend/screens/PasswordReset.png 'Home')

_Home (Logged In) screen_

---

### Ontology View

On the Ontology View screen, the maintainer can upload an ontology, which is then displayed as a graph. The ontology can be updated, or two versions of the ontology can be compared, with the differences between them displayed. By clicking on the elements in the graph, detailed information is shown.

[![OntologyView1](../../media/frontend/screens/OntologyView1.png 'OntologyView1')](../../media/frontend/screens/OntologyView1.png 'OntologyView1')

[![OntologyView2](../../media/frontend/screens/OntologyView2.png 'OntologyView2')](../../media/frontend/screens/OntologyView2.png 'OntologyView2')

[![OntologyView3](../../media/frontend/screens/OntologyView3.png 'OntologyView3')](../../media/frontend/screens/OntologyView3.png 'OntologyView3')

_Ontology View screens_

---

### Ontology Upload

On the Ontology Upload screen, the user first enters the study data and can then upload several codebooks in CSV format sequentially. The information from the codebooks is displayed in a table, where the user can modify it by moving or deleting rows, changing header text, or deleting columns. If available, the backend assigns a questionnaire item for each question in the codebook. The user can confirm this selection, select a different item if there are several items, or deselect defaults. All data is then submitted for review.

[![OntologyUpload1](../../media/frontend/screens/OntologyUpload1.png 'OntologyUpload1')](../../media/frontend/screens/OntologyUpload1.png 'OntologyUpload1')

[![OntologyUpload2](../../media/frontend/screens/OntologyUpload2.png 'OntologyUpload2')](../../media/frontend/screens/OntologyUpload2.png 'OntologyUpload2')

_Ontology Upload screens_

---

### Ontology Review

On the Ontology Review screen, the maintainer can apply open submissions or review the submission assigned to them. For each decision status, the maintainer can add a comment that is visible to the user on the feedback screen. Each submission contains the study details, changes to the ontology and the associated migration processes. In the Ontology changes section, the ontology diagram is displayed, with detailed information displayed when a selection is made. The legend provides information about the color coding within the diagram. Selected migration operations are also displayed in the graph. For each review status decision, the maintainer can add a comment that is visible to the user on the feedback screen.

[![OntologyReview1](../../media/frontend/screens/OntologyReview1.png 'OntologyReview1')](../../media/frontend/screens/OntologyReview1.png 'OntologyReview1')

[![OntologyReview2](../../media/frontend/screens/OntologyReview2.png 'OntologyReview2')](../../media/frontend/screens/OntologyReview2.png 'OntologyReview2')

[![OntologyReview3](../../media/frontend/screens/OntologyReview3.png 'OntologyReview3')](../../media/frontend/screens/OntologyReview3.png 'OntologyReview3')

_Ontology Review screens_

---

### Data Upload

On the Data Upload screen, the user uploads the data for the codebook of their study. Metadata is displayed based on the column selection. Before submission, a data quality check must be performed and completed. The results are then displayed. If errors are found, they must be corrected in the file, and the file must be reuploaded. Only when the data quality check has been successfully completed for all submissions can the data upload proceed.

[![DataUpload1](../../media/frontend/screens/DataUpload1.png 'DataUpload1')](../../media/frontend/screens/DataUpload1.png 'DataUpload1')

[![DataUpload2](../../media/frontend/screens/DataUpload2.png 'DataUpload2')](../../media/frontend/screens/DataUpload2.png 'DataUpload2')

[![DataUpload3](../../media/frontend/screens/DataUpload3.png 'DataUpload3')](../../media/frontend/screens/DataUpload3.png 'DataUpload3')

[![DataUpload4](../../media/frontend/screens/DataUpload4.png 'DataUpload4')](../../media/frontend/screens/DataUpload4.png 'DataUpload4')

[![DataUpload5](../../media/frontend/screens/DataUpload5.png 'DataUpload5')](../../media/frontend/screens/DataUpload5.png 'DataUpload5')

_DataUpload screens_

---

### Data Review

On the Data Review screen, the maintainer reviews the submissions made by the user. Each submission includes study details, data, and the ontology graph, which are displayed accordingly. The review is completed by setting the review status, and a comment can be added to each decision, which will later be visible to the user on the feedback screen.

[![DataReview1](../../media/frontend/screens/DataReview1.png 'DataReview1')](../../media/frontend/screens/DataReview1.png 'DataReview1')

[![DataReview2](../../media/frontend/screens/DataReview2.png 'DataReview2')](../../media/frontend/screens/DataReview2.png 'DataReview2')

[![DataReview3](../../media/frontend/screens/DataReview3.png 'DataReview3')](../../media/frontend/screens/PasswordReset.png 'DataReview3')

_Data Review screens_

---

### Data View

On the Data View screen, the user sees their submissions, including the study information and the submitted data. The data quality can also be checked and the results are then displayed in detail.

[![DataView1](../../media/frontend/screens/DataView1.png 'DataView1')](../../media/frontend/screens/DataView1.png 'DataView1')

[![DataView2](../../media/frontend/screens/DataView2.png 'DataView2')](../../media/frontend/screens/DataView2.png 'DataView2')

[![DataView3](../../media/frontend/screens/DataView3.png 'DataView3')](../../media/frontend/screens/DataView3.png 'DataView3')

[![DataView4](../../media/frontend/screens/DataView4.png 'DataView4')](../../media/frontend/screens/DataView4.png 'DataView4')

_Data View screens_

---

### Data Export

On the Data Export screen, the user selects a metadata field in the graph and performs a query to find related items. The found item can then be added to the export. This step can be repeated multiple times, allowing different items to be selected for export. Once all items are selected, the export configuration is set, and the data is prepared for download.

[![DataExport1](../../media/frontend/screens/DataExport1.png 'DataExport1')](../../media/frontend/screens/DataExport1.png 'DataExport1')

[![DataExport2](../../media/frontend/screens/DataExport2.png 'DataExport2')](../../media/frontend/screens/DataExport2.png 'DataExport2')

[![DataExport3](../../media/frontend/screens/DataExport3.png 'DataExport3')](../../media/frontend/screens/DataExport3.png 'DataExport3')

_Data Export screens_

---

### Profile

On the Profile screen, the user can view the information about the submitted ontologies and data for the respective study as well as the review status.

[![Profile](../../media/frontend/screens/Profile.png 'Profile')](../../media/frontend/screens/Profile.png 'Profile')

_Profile screen_

---

### Feedback

In the Feedback screen, the user can view the review feedback on the submitted ontologies and data of the respective study. The submitted study information and ontologies or data are also displayed, with multiple items shown in individual tabs.

[![Feedback1](../../media/frontend/screens/Feedback1.png 'Feedback1')](../../media/frontend/screens/Feedback1.png 'Feedback1')

[![Feedback2](../../media/frontend/screens/Feedback2.png 'Feedback2')](../../media/frontend/screens/Feedback2.png 'Feedback2')

_Feedback screens_

---

### Admin

On the Admin screen, the registered users are listed. The displayed information comes from the data provided by the user during registration. The admin can modify this information, grant the requested access rights, or remove the user. Additionally, they can resend the verification email or reset the user's password.

[![Admin1](../../media/frontend/screens/Admin1.png 'Admin1')](../../media/frontend/screens/Admin1.png 'Admin1')

[![Admin2](../../media/frontend/screens/Admin2.png 'Admin2')](../../media/frontend/screens/Admin2.png 'Admin2')

_Admin screens_

---

### Not Found (404)

On the Not Found (404) screen, the user is informed that the requested page could not be found. The 'Back' button redirects the user to the last screen or the homepage.

[![404](../../media/frontend/screens/404.png '404')](../../media/frontend/screens/404.png '404')

_Not Found screen_
