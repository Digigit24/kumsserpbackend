# Approval & Notification System API Documentation

## Overview

The **Approval & Notification System** provides a comprehensive workflow for managing approval requests across your KUMSS ERP system. The primary use case is **fee payment approval**, where students submit fee payments that require approval from teachers/admins before the receipt can be downloaded.

---

## 🎯 **Key Features**

✅ **Generic Approval System** - Can handle any type of approval (fees, documents, leaves, etc.)
✅ **Multi-level Approvals** - Support for multiple approvers
✅ **Real-time Notifications** - In-app notifications for all stakeholders
✅ **Approval Tracking** - Complete audit trail of all actions
✅ **Priority Levels** - Low, Medium, High, Urgent
✅ **Deadline Management** - Set deadlines for approvals
✅ **Auto-notifications** - Automatic notifications on status changes

---

## 🔄 **Fee Payment Approval Workflow**

### **Step 1: Student Pays Fee**
Student submits a fee payment → Creates approval request → Notifies teachers/admins

### **Step 2: Teacher/Admin Reviews**
Teachers/admins see pending approvals → Review and approve/reject

### **Step 3: Student Gets Notified**
Student receives notification → Can download receipt if approved

---

## 📍 **API Endpoints**

Base URL: `http://localhost:8000/api/v1/approvals/`

### **1. Approval Requests**

#### **Get All Approval Requests**
```
GET /api/v1/approvals/requests/
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "Fee Payment Approval - ₹50000.00",
      "request_type": "fee_payment",
      "request_type_display": "Fee Payment",
      "status": "pending",
      "status_display": "Pending",
      "priority": "high",
      "priority_display": "High",
      "requester_details": {
        "id": 5,
        "username": "student123",
        "email": "student@example.com",
        "full_name": "John Doe"
      },
      "approvers_details": [
        {
          "id": 2,
          "username": "teacher1",
          "email": "teacher@example.com",
          "full_name": "Jane Teacher"
        }
      ],
      "submitted_at": "2025-12-31T10:00:00Z",
      "deadline": "2025-12-31T18:00:00Z",
      "is_overdue": false,
      "metadata": {
        "fee_collection_id": 123,
        "amount": "50000.00",
        "payment_date": "2025-12-31"
      }
    }
  ]
}
```

---

#### **Get My Approval Requests**
Get all requests made by the current user.

```
GET /api/v1/approvals/requests/my_requests/
```

---

#### **Get Pending Approvals**
Get all pending requests that need the current user's approval.

```
GET /api/v1/approvals/requests/pending_approvals/
```

---

#### **Review Approval Request (Approve/Reject)**
```
POST /api/v1/approvals/requests/{id}/review/
```

**Request Body:**
```json
{
  "action": "approve",  // or "reject"
  "comment": "Payment verified. Approved."
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Fee Payment Approval - ₹50000.00",
  "status": "approved",
  "status_display": "Approved",
  "reviewed_at": "2025-12-31T11:00:00Z",
  "actions": [
    {
      "id": 1,
      "actor_details": {
        "id": 2,
        "username": "teacher1",
        "full_name": "Jane Teacher"
      },
      "action": "approve",
      "action_display": "Approved",
      "comment": "Payment verified. Approved.",
      "actioned_at": "2025-12-31T11:00:00Z"
    }
  ]
}
```

---

### **2. Fee Payment Approval**

#### **Submit Fee Payment for Approval**
```
POST /api/v1/approvals/fee-payment/
```

**Request Body:**
```json
{
  "fee_collection_id": 123,
  "title": "Fee Payment Approval - Semester 1",
  "description": "Tuition fee payment for Semester 1",
  "priority": "high",
  "approver_ids": [2, 3],  // Teacher/Admin user IDs
  "deadline_hours": 24,
  "attachment": null  // Optional file upload
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Fee Payment Approval - Semester 1",
  "request_type": "fee_payment",
  "status": "pending",
  "requester_details": {
    "id": 5,
    "full_name": "John Doe"
  },
  "approvers_details": [
    {
      "id": 2,
      "full_name": "Jane Teacher"
    },
    {
      "id": 3,
      "full_name": "Admin User"
    }
  ],
  "submitted_at": "2025-12-31T10:00:00Z",
  "deadline": "2026-01-01T10:00:00Z"
}
```

---

### **3. Notifications**

#### **Get All Notifications**
```
GET /api/v1/approvals/notifications/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "notification_type": "approval_approved",
      "notification_type_display": "Approval Approved",
      "title": "Your Fee Payment request has been approved",
      "message": "Your request \"Fee Payment Approval - ₹50000.00\" has been approved by Jane Teacher.",
      "priority": "high",
      "is_read": false,
      "read_at": null,
      "sent_at": "2025-12-31T11:00:00Z",
      "action_url": "/approvals/1"
    }
  ]
}
```

---

#### **Get Unread Notifications**
```
GET /api/v1/approvals/notifications/unread/
```

---

#### **Get Unread Count**
```
GET /api/v1/approvals/notifications/unread_count/
```

**Response:**
```json
{
  "unread_count": 3
}
```

---

#### **Mark Notifications as Read**
```
POST /api/v1/approvals/notifications/mark_read/
```

**Request Body (Mark specific notifications):**
```json
{
  "notification_ids": [1, 2, 3]
}
```

**Request Body (Mark all as read):**
```json
{}
```

**Response:**
```json
{
  "marked_count": 3
}
```

---

#### **Mark Single Notification as Read**
```
POST /api/v1/approvals/notifications/{id}/read/
```

---

### **4. Bulk Notifications (Admin/Teacher Only)**

#### **Send Bulk Notifications**
```
POST /api/v1/approvals/notifications/bulk/
```

**Request Body:**
```json
{
  "recipient_ids": [5, 6, 7, 8],
  "notification_type": "general",
  "title": "Fee Payment Deadline Reminder",
  "message": "Please submit your semester fee payment by January 15th.",
  "priority": "medium",
  "action_url": "/fees/payment",
  "expires_at": "2026-01-15T23:59:59Z"
}
```

**Response:**
```json
{
  "created_count": 4
}
```

---

## 🎯 **Use Case Examples**

### **Example 1: Student Submits Fee Payment for Approval**

**Frontend (Student Panel):**
```javascript
// After student uploads payment receipt
const formData = new FormData();
formData.append('file', receiptFile);
formData.append('folder', 'fee_receipts');

// Upload receipt to S3
const uploadResponse = await fetch('/api/v1/core/upload/single/', {
  method: 'POST',
  headers: { 'Authorization': `Token ${token}` },
  body: formData
});

const { file_url, s3_key } = await uploadResponse.json();

// Submit for approval
const approvalResponse = await fetch('/api/v1/approvals/fee-payment/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    fee_collection_id: 123,
    title: "Semester Fee Payment - ₹50000",
    description: "Payment receipt uploaded",
    priority: "high",
    approver_ids: [2, 3],  // Teacher and Admin IDs
    deadline_hours: 48
  })
});

// Success! Student gets confirmation
alert("Payment submitted for approval!");
```

---

### **Example 2: Teacher Approves Fee Payment**

**Frontend (Teacher Panel):**
```javascript
// Get pending approvals
const response = await fetch('/api/v1/approvals/requests/pending_approvals/', {
  headers: { 'Authorization': `Token ${token}` }
});

const { results } = await response.json();

// Show list of pending approvals
results.forEach(approval => {
  console.log(
    `${approval.requester_details.full_name} -
     ${approval.title} -
     ₹${approval.metadata.amount}`
  );
});

// Approve a payment
const approveResponse = await fetch(`/api/v1/approvals/requests/${approvalId}/review/`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    action: "approve",
    comment: "Payment verified and approved"
  })
});

// Success! Notification sent to student automatically
```

---

### **Example 3: Student Checks Notification and Downloads Receipt**

**Frontend (Student Panel):**
```javascript
// Check for new notifications
const notifResponse = await fetch('/api/v1/approvals/notifications/unread/', {
  headers: { 'Authorization': `Token ${token}` }
});

const { results } = await notifResponse.json();

// Show notifications
results.forEach(notif => {
  if (notif.notification_type === 'approval_approved') {
    showNotification(
      'Payment Approved!',
      'Your fee payment has been approved. You can now download the receipt.',
      'success'
    );

    // Enable receipt download button
    enableReceiptDownload();
  }
});

// Mark notification as read
await fetch(`/api/v1/approvals/notifications/${notif.id}/read/`, {
  method: 'POST',
  headers: { 'Authorization': `Token ${token}` }
});
```

---

## 📊 **Database Models**

### **ApprovalRequest**
- Stores all approval requests
- Generic foreign key - can link to any model (FeeCollection, Document, etc.)
- Tracks status, priority, deadline
- Supports multi-level approvals

### **ApprovalAction**
- Audit trail of all approval/rejection actions
- Tracks who did what when
- Includes IP address for security

### **Notification**
- In-app notifications
- Links to approval requests or other objects
- Read/unread tracking
- Expiry support

---

## 🔒 **Permissions & Access Control**

### **Students:**
- Can create approval requests (fee payments)
- Can view their own requests
- Can view their notifications
- Cannot review other approvals

### **Teachers/Admins:**
- Can view pending approvals assigned to them
- Can approve/reject requests
- Can send bulk notifications
- Can view all approval history

---

## 🎨 **Frontend Integration Guide**

### **1. Display Pending Approvals Badge**
```javascript
// Get unread count for badge
const { unread_count } = await fetch('/api/v1/approvals/notifications/unread_count/');

// Show badge
<Bell icon with badge showing unread_count />
```

### **2. Real-time Updates (Optional)**
Use WebSockets or polling to get real-time notification updates:

```javascript
// Poll every 30 seconds
setInterval(async () => {
  const { results } = await fetch('/api/v1/approvals/notifications/unread/');
  updateNotificationUI(results);
}, 30000);
```

### **3. Notification Component**
```jsx
function NotificationList() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    const res = await fetch('/api/v1/approvals/notifications/unread/');
    const data = await res.json();
    setNotifications(data.results);
  };

  const markAsRead = async (id) => {
    await fetch(`/api/v1/approvals/notifications/${id}/read/`, {
      method: 'POST'
    });
    fetchNotifications();
  };

  return (
    <div>
      {notifications.map(notif => (
        <NotificationCard
          key={notif.id}
          notification={notif}
          onRead={() => markAsRead(notif.id)}
        />
      ))}
    </div>
  );
}
```

---

## ⚙️ **Backend Setup Instructions**

### **1. Install & Run Migrations**
```bash
# The user needs to run these on their local machine
python manage.py makemigrations approvals
python manage.py migrate
```

### **2. Create Approval Workflow**
The signals automatically create notifications when:
- Approval request is created → Notifies approvers
- Approval is approved/rejected → Notifies requester

### **3. Customize for Your Needs**
The approval system is generic and can be extended:
- Add new request types (document_verification, leave_request, etc.)
- Customize notification templates
- Add email/SMS notifications using communication app

---

## 🚀 **Quick Start Checklist**

- ✅ Approval app created and added to INSTALLED_APPS
- ✅ URL routing configured (`/api/v1/approvals/`)
- ✅ Models created (ApprovalRequest, ApprovalAction, Notification)
- ✅ API endpoints ready to use
- ✅ Auto-notifications configured via signals
- ⚠️ **YOU NEED TO:** Run migrations on your local machine
- ⚠️ **YOU NEED TO:** Integrate with frontend

---

## 📝 **Summary**

This approval system provides a complete workflow for managing approvals across your ERP:

1. **Students** submit fee payments → Creates approval requests
2. **Teachers/Admins** receive notifications → Review and approve/reject
3. **Students** get notified → Can download receipt if approved

All with full audit trails, real-time notifications, and a clean API! 🎉

---

## 🆘 **Support**

For issues or questions:
- Check the API documentation above
- Review the model definitions in `apps/approvals/models.py`
- Check the view implementations in `apps/approvals/views.py`
