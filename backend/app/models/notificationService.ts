import axios from "axios";

const API_URL = "/notifications";

export const getNotifications = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const markAsRead = async (id: number) => {
  await axios.put(`${API_URL}/${id}/read`);
};
