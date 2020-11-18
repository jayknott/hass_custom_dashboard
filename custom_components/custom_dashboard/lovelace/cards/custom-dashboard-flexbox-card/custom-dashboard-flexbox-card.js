import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

const VERSION = "0.1.3";

const createError = (error, config) => {
  return createThing("hui-error-card", {
    type: "error",
    error,
    config,
  });
};

const cardHelpers = window.loadCardHelpers()
  ? window.loadCardHelpers()
  : undefined;

const createThing = async (tag, config) => {
  if (cardHelpers) {
    const cardHelper = await cardHelpers;
    return cardHelper.createCardElement(config);
  }

  const element = document.createElement(tag);

  try {
    element.setConfig(config);
  } catch (err) {
    console.error(tag, err);
    return createError(err.message, config);
  }

  return element;
};

class CustomDashboardFlexboxCard extends LitElement {
  constructor() {
    super();
  }

  static get properties() {
    return {
      _config: {},
      _refCards: {},
    };
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._refCards && this._config) {
      this.renderCard();
    }
    if (this._refCards) {
      this._refCards.forEach((card) => {
        card.hass = hass;
      });
    }
  }


  setConfig(config) {
    if (!config || !config.cards || !Array.isArray(config.cards)) {
      throw new Error("Card config incorrect");
    }

    this._config = {
      item_width: 0,
      item_height: 0,
      grid_margin: 10,
      card_padding: 0,
      margin_bottom: '20px',
      unit: 'px',
      ...config
    };

    if (this._hass) {
      this.renderCard();
    }
  }

  renderCard() {
    const cards = this._config.cards;

    const promises = cards.map((card) => this.createCardElement(card.card));
    Promise.all(promises).then((card_objects) => {
      this._refCards = card_objects;
    });
  }

  async createCardElement(cardConfig) {
    let tag = cardConfig.type;

    if (tag.startsWith("divider")) {
      tag = `hui-divider-row`;
    } else if (tag.startsWith("custom:")) {
      tag = tag.substr("custom:".length);
    } else {
      tag = `hui-${tag}-card`;
    }

    const element = await createThing(tag, cardConfig);

    if (cardConfig.item_classes) {
      element.className = "item " + cardConfig.item_classes;
    } else {
      if (this._config.items_classes) {
        element.className = "item " + this._config.items_classes;
      } else {
        element.className = "item";
      }
    }

    element.hass = this._hass;

    element.addEventListener(
      "ll-rebuild",
      (ev) => {
        ev.stopPropagation();
        this.createCardElement(cardConfig).then(() => {
          this.renderCard();
        });
      },
      { once: true }
    );

    return element;
  }

  render() {
    if (!this._config || !this._hass || !this._refCards) {
      return html``;
    }

    const {
      cards = [],
      grid_margin = 10,
      item_height = 0,
      item_width = 0,
      margin_bottom= '20px',
      padding = 0,
      unit = 'px'
    } = this._config;

    const items = this._refCards.map((card, card_i) => {

      // Do not render hidden condition cards
      if (card && card.style && card.style.display && card.style.display == 'none') {
        return '';
      }

      const card_config = {
        column_span: 1,
        row_span: 1,
        ...(cards[card_i])
      };
      let col = '';
      let row = '';
      if (card_config.column_span >= 1) {
        const width = (item_width * card_config.column_span) + (grid_margin * (card_config.column_span - 1));
        col = `width:${width == 0 ? 'auto' : width.toString() + unit};`;
      }
      if (card_config.row_span >= 1) {
        const height = (item_height * card_config.row_span) + (grid_margin * (card_config.row_span - 1));
        row = `height:${height == 0 ? 'auto' : height.toString() + unit};`;
      }

      return html`
        <li style="margin-right:${grid_margin}${unit};margin-bottom:${grid_margin}${unit};${col}${row}">
          ${card}
        </li>
      `
    });

    return html`
      <ul class="flex-container" style="padding: ${padding}${unit};margin-bottom: ${margin_bottom}">
        ${items}
      </ul>
    `;
  }

  static get styles() {
    return [
      css`
        .flex-container {
          padding: 0;
          margin: 0 0 0 0;
          list-style: none;
          -ms-box-orient: horizontal;
          display: -webkit-box;
          display: -moz-box;
          display: -ms-flexbox;
          display: -moz-flex;
          display: -webkit-flex;
          display: flex;
          -webkit-flex-wrap: wrap;
          flex-wrap: wrap;
        }
      `,
    ];
  }

  getCardSize() {
    return 3;
  }
}

if (!customElements.get("custom-dashboard-flexbox-card")) {
  customElements.define("custom-dashboard-flexbox-card", CustomDashboardFlexboxCard);
  console.info(
    `%c  CUSTOM-DASHBOARD-FLEXBOX-CARD         \n%c  Version ${VERSION}                         `,
    "color: #2fbae5; font-weight: bold; background: black",
    "color: white; font-weight: bold; background: dimgray"
  );
}
