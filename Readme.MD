# 🚀 Atlassian Directory Automation

## 🎯 Objective

Automate the process of fetching and parsing the list of users, groups, and group memberships in an Atlassian account using **Python** and **Playwright**.

---

## 📝 Prerequisites

1. **Atlassian Account**
   - Create a new account at [admin.atlassian.com](https://admin.atlassian.com).
   - Add at least **50 users** and **25 groups** (fake data with domain `example.com` is acceptable).
2. **Python Environment**
   - Python 3.8+
   - Ubuntu (recommended, but scripts work on any OS with Python and Playwright)
3. **Excel Files**
   - For user/group creation, place `User.xlsx` and `Group.xlsx` in the `Data/` folder.

---

## 📁 File Structure

<details>
<summary>Click to expand project directory structure</summary>

```
IDEN-2/
├── Data/
│   ├── User.xlsx              # 📄 Excel file with user emails and group assignments
│   └── Group.xlsx             # 📄 Excel file with group names
├── Outputs/
│   ├── Users_Result.json      # 🗂️ Output: List of users and their group memberships
│   └── Groups_Result.json     # 🗂️ Output: List of groups and their members
├── Group_Adding.py            # 🤖 Script to automate group creation from Excel
├── Group_Getter.py            # 🤖 Script to fetch group details and members
├── User_Adding.py             # 🤖 Script to automate user invitations from Excel
├── User_Getter.py             # 🤖 Script to fetch user details and group memberships
├── Requirements.txt           # 📦 Python dependencies
├── .env                       # 🔑 Environment variables (see below)
├── .gitignore                 # 🚫 Ignore venv and .env
└── Readme.MD                  # 📚 Project documentation
```

</details>

---

## 🔑 .env File Example

Create a `.env` file in the project root with the following keys:

```
ATLASSIAN_URL=https://admin.atlassian.com
ATLASSIAN_USERNAME=your-email@example.com
ATLASSIAN_PASSWORD=your-password
```

- `ATLASSIAN_URL`: Atlassian admin portal URL.
- `ATLASSIAN_USERNAME`: Your Atlassian admin email.
- `ATLASSIAN_PASSWORD`: Your Atlassian admin password.

---

## ⚙️ Setup Instructions

```bash
# Update system and install dependencies
sudo apt update && sudo apt upgrade -y

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required Python packages
pip install -r Requirements.txt

# Install Playwright browsers
python3 -m playwright install
```

---

## 🛠️ Script Descriptions

- **User_Getter.py**  
  Automates login and fetches user details (id, name, email, status, last active, groups) and saves to `Outputs/Users_Result.json`.

- **Group_Getter.py**  
  Automates login and fetches group details (id, name, description, members) and saves to `Outputs/Groups_Result.json`.

- **User_Adding.py**  
  Automates inviting users and assigning them to groups using data from `Data/User.xlsx`.

- **Group_Adding.py**  
  Automates creation of groups using data from `Data/Group.xlsx`.

---

## 📦 Output Format

- **Users_Result.json**

  ```json
  [
    {
      "Id": "user-id",
      "Name": "User Name",
      "Email": "user@example.com",
      "Status": "active/suspended",
      "Last Seen": "timestamp",
      "Groups": ["Group1", "Group2"]
    },
    ...
  ]
  ```

- **Groups_Result.json**
  ```json
  [
    {
      "Id": "group-id",
      "Name": "Group Name",
      "Description": "Group Description",
      "Members": ["User1", "User2"]
    },
    ...
  ]
  ```

---

## ✨ Key Features

- ⚡ Uses Playwright for browser automation and network request interception.
- 📚 Handles pagination to fetch all users/groups.
- 🗂️ Parses API responses and outputs structured JSON.
- 🤖 Scripts for automating user and group creation from Excel files.
- 📝 Well-commented code for clarity and maintainability.

---

## ⚠️ Notes

- 🔄 For large datasets, ensure pagination logic is implemented.
- 🧑‍💻 All scripts are designed for educational and assessment purposes.

---

## 👨‍💻 Author

Integration Engineer Assessment: Atlassian Sync
