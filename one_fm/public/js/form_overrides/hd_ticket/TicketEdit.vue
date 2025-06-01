<template>
  <div class="flex h-screen">
    <Sidebar />

    <div class="flex flex-col w-full overflow-y-auto">
      <LayoutHeader>
        <template #left-header>
          <Breadcrumbs :items="breadcrumbs" />
        </template>
      </LayoutHeader>

      <div class="flex flex-col gap-5 py-6 h-full flex-1 self-center overflow-auto mx-auto w-full max-w-4xl px-5">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <!-- Subject -->
          <div class="flex flex-col gap-2">
            <label class="text-sm text-gray-700">Subject</label>
            <FormControl v-model="subject" type="text" placeholder="Ticket subject" />
          </div>

          <!-- Type -->
          <div class="flex flex-col gap-2">
            <label class="text-sm text-gray-700">Type</label>
            <select
              v-model="type"
              class="form-select border rounded px-3 py-2 min-h-[42px] focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Select type</option>
              <option v-for="item in types" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>

          <!-- Priority -->
          <div class="flex flex-col gap-2">
            <label class="text-sm text-gray-700">Priority</label>
            <select
              v-model="priority"
              class="form-select border rounded px-3 py-2 min-h-[42px] focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Select priority</option>
              <option v-for="item in priorities" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>

          <!-- Process -->
          <div class="flex flex-col gap-2">
            <label class="text-sm text-gray-700">Process</label>
            <select
              v-model="process"
              class="form-select border rounded px-3 py-2 min-h-[42px] focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Select process</option>
              <option v-for="item in processes" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
        </div>

        <!-- Editor -->
        <TicketTextEditor
          ref="editor"
          v-model:attachments="attachments"
          v-model:content="description"
          placeholder="Ticket description"
          expand
        >
          <template #bottom-right>
            <Button
              label="Update Ticket"
              theme="gray"
              variant="solid"
              :disabled="!ticketName || !type || !priority || $refs.editor?.editor.isEmpty"
              @click="submitUpdate"
            />
          </template>
        </TicketTextEditor>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import Sidebar from "@/components/layouts/Sidebar.vue";
import { Breadcrumbs, Button, call, FormControl, usePageMeta } from "frappe-ui";
import TicketTextEditor from "./TicketTextEditor.vue";
import { onMounted, ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const ticketName = route.params.ticket_name as string | undefined;

const subject = ref("");
const description = ref("");
const type = ref("");
const priority = ref("");
const process = ref("");
const attachments = ref([]);

const types = ref<string[]>([]);
const priorities = ref<string[]>([]);
const processes = ref<string[]>([]);

async function fetchOptions(endpoint: string, targetRef: typeof ref<string[]>) {
  try {
    const res = await call(endpoint);
    if (res.status_code === 200) {
      targetRef.value = res.data;
    }
  } catch (e) {
    console.error(`Failed to fetch ${endpoint}`, e);
  }
}

onMounted(async () => {
  await fetchOptions("one_fm.overrides.hd_ticket.get_ticket_type", types);
  await fetchOptions("one_fm.overrides.hd_ticket.get_priority", priorities);
  await fetchOptions("one_fm.overrides.hd_ticket.get_process", processes);

  if (!ticketName) return;

  try {
    const res = await call("one_fm.overrides.hd_ticket.get_ticket_details", {
      name: ticketName,
    });
    const data = res.data;
    subject.value = data.subject || "";
    description.value = data.description || "";
    type.value = data.type || "";
    priority.value = data.priority || "";
    process.value = data.process || "";
  } catch (e) {
    console.error("Failed to fetch ticket data", e);
  }
});

async function submitUpdate() {
  if (!ticketName) return;

  try {
    await call("one_fm.overrides.hd_ticket.update_ticket", {
      name: ticketName,
      updates: JSON.stringify({
        subject: subject.value,
        description: description.value,
        type: type.value,
        priority: priority.value,
        process: process.value,
        attachments: attachments.value,
      }),
    });
    router.push({ name: "TicketDetails", params: { ticket_name: ticketName } });
  } catch (e) {
    console.error("Update failed", e);
  }
}

const breadcrumbs = computed(() => [
  { label: "Tickets", route: { name: "TicketsCustomer" } },
  { label: "Edit Ticket", route: route.fullPath },
]);

usePageMeta(() => ({
  title: "Edit Ticket",
}));
</script>

<style scoped>
.form-select {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: white;
  appearance: none;
}
</style>
