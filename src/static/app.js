document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build activity card content safely using DOM APIs
        const titleEl = document.createElement("h4");
        titleEl.textContent = name;

        const descriptionEl = document.createElement("p");
        descriptionEl.textContent = details.description;

        const scheduleEl = document.createElement("p");
        const scheduleStrong = document.createElement("strong");
        scheduleStrong.textContent = "Schedule:";
        scheduleEl.appendChild(scheduleStrong);
        scheduleEl.appendChild(document.createTextNode(" " + details.schedule));

        const availabilityEl = document.createElement("p");
        const availabilityStrong = document.createElement("strong");
        availabilityStrong.textContent = "Availability:";
        availabilityEl.appendChild(availabilityStrong);
        availabilityEl.appendChild(document.createTextNode(" " + spotsLeft + " spots left"));

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsLabel = document.createElement("strong");
        if (details.participants.length > 0) {
          participantsLabel.textContent = `Currently Signed Up (${details.participants.length}):`;
          participantsSection.appendChild(participantsLabel);

          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";

          details.participants.forEach(email => {
            const li = document.createElement("li");

            const emailSpan = document.createElement("span");
            emailSpan.className = "participant-email";
            emailSpan.textContent = email;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.title = "Remove participant";
            deleteBtn.textContent = "✕";
            deleteBtn.dataset.activity = name;
            deleteBtn.dataset.email = email;

            li.appendChild(emailSpan);
            li.appendChild(deleteBtn);
            participantsList.appendChild(li);
          });

          participantsSection.appendChild(participantsList);
        } else {
          participantsLabel.textContent = "Currently Signed Up:";
          participantsSection.appendChild(participantsLabel);

          const noParticipantsMsg = document.createElement("p");
          noParticipantsMsg.className = "no-participants";
          noParticipantsMsg.textContent = "No students yet - be the first!";
          participantsSection.appendChild(noParticipantsMsg);
        }

        // Append all parts to the activity card
        activityCard.appendChild(titleEl);
        activityCard.appendChild(descriptionEl);
        activityCard.appendChild(scheduleEl);
        activityCard.appendChild(availabilityEl);
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners for delete buttons
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleDeleteParticipant);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle delete participant
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const activityName = event.target.getAttribute('data-activity');
    const email = event.target.getAttribute('data-email');

    if (!confirm(`Remove ${email} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh the activities list
        await fetchActivities();
        
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
      } else {
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 3 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 3000);
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Refresh activities list to show updated participant count
      if (response.ok) {
        await fetchActivities();
      }

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
