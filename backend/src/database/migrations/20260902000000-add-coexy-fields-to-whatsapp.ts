import { QueryInterface, DataTypes } from "sequelize";

module.exports = {
  up: (queryInterface: QueryInterface) => {
    return Promise.all([
      queryInterface.addColumn("Whatsapps", "coexy_channel_id", {
        type: DataTypes.STRING,
        allowNull: true,
        defaultValue: null
      }),
      queryInterface.addColumn("Whatsapps", "coexy_channel_token", {
        type: DataTypes.STRING,
        allowNull: true,
        defaultValue: null
      }),
      queryInterface.addColumn("Whatsapps", "coexy_connect_url", {
        type: DataTypes.TEXT,
        allowNull: true,
        defaultValue: null
      }),
      queryInterface.addColumn("Whatsapps", "coexy_status", {
        type: DataTypes.STRING,
        allowNull: true,
        defaultValue: null
      })
    ]);
  },

  down: (queryInterface: QueryInterface) => {
    return Promise.all([
      queryInterface.removeColumn("Whatsapps", "coexy_channel_id"),
      queryInterface.removeColumn("Whatsapps", "coexy_channel_token"),
      queryInterface.removeColumn("Whatsapps", "coexy_connect_url"),
      queryInterface.removeColumn("Whatsapps", "coexy_status")
    ]);
  }
};
